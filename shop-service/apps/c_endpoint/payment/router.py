import os
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from apps.common.auth import get_current_user
from domain.order import get_order_detail
from domain.order.order_service import pay_order
from common.exceptions import BusinessError, NotFoundError

router = APIRouter(prefix="/c-endpoint/payment", tags=["C端-支付"])

# 支付宝配置（从环境变量读取）
ALIPAY_APP_ID = os.getenv("ALIPAY_APP_ID", "")
ALIPAY_APP_PRIVATE_KEY = os.getenv("ALIPAY_APP_PRIVATE_KEY", "")
ALIPAY_ALIPAY_PUBLIC_KEY = os.getenv("ALIPAY_ALIPAY_PUBLIC_KEY", "")
ALIPAY_NOTIFY_URL = os.getenv("ALIPAY_NOTIFY_URL", "")
ALIPAY_RETURN_URL = os.getenv("ALIPAY_RETURN_URL", "http://localhost:5173/payment/__ORDER_ID__?from=alipay")


def _format_private_key(key: str) -> str:
    """自动给应用私钥补全 BEGIN/END 标记（兼容用户从沙箱直接复制纯 base64 密钥）"""
    key = key.strip()
    if "BEGIN" in key and "END" in key:
        return key
    # 支付宝沙箱默认提供 PKCS#1 格式私钥，补全 RSA 私钥标记
    return (
        "-----BEGIN RSA PRIVATE KEY-----\n"
        + key
        + "\n-----END RSA PRIVATE KEY-----"
    )


def _format_public_key(key: str) -> str:
    """自动给支付宝公钥补全 BEGIN/END 标记"""
    key = key.strip()
    if "BEGIN" in key and "END" in key:
        return key
    return (
        "-----BEGIN PUBLIC KEY-----\n"
        + key
        + "\n-----END PUBLIC KEY-----"
    )


def _get_alipay_client():
    """创建支付宝沙箱客户端"""
    AliPay = None
    import_error = None

    # 尝试多种导入方式（兼容不同 pip 包名安装后的模块名）
    for module_name in ("alipay", "python_alipay_sdk"):
        try:
            mod = __import__(module_name, fromlist=["AliPay"])
            AliPay = getattr(mod, "AliPay", None)
            if AliPay:
                break
        except ImportError as e:
            import_error = e

    if AliPay is None:
        raise BusinessError(
            "支付宝SDK未安装。请在 shop-service 容器中执行：\n"
            "pip install python-alipay-sdk\n"
            f"原始错误: {import_error}"
        )

    # 检查配置是否完整
    if not ALIPAY_APP_ID:
        raise BusinessError("支付宝沙箱未配置：缺少 ALIPAY_APP_ID，请在 .env 文件中填入沙箱应用ID")
    if not ALIPAY_APP_PRIVATE_KEY:
        raise BusinessError("支付宝沙箱未配置：缺少 ALIPAY_APP_PRIVATE_KEY，请在 .env 文件中填入应用私钥")
    if not ALIPAY_ALIPAY_PUBLIC_KEY:
        raise BusinessError("支付宝沙箱未配置：缺少 ALIPAY_ALIPAY_PUBLIC_KEY，请在 .env 文件中填入支付宝公钥")

    private_key = _format_private_key(ALIPAY_APP_PRIVATE_KEY)
    public_key = _format_public_key(ALIPAY_ALIPAY_PUBLIC_KEY)

    return AliPay(
        appid=ALIPAY_APP_ID,
        app_notify_url=ALIPAY_NOTIFY_URL,
        app_private_key_string=private_key,
        alipay_public_key_string=public_key,
        sign_type="RSA2",
        debug=True,  # 沙箱模式
    )


@router.get("/alipay/page-pay/{order_id}")
def alipay_page_pay(order_id: int, user: dict = Depends(get_current_user)):
    """
    支付宝电脑网站支付（页面跳转）
    返回支付宝支付页面 URL，前端跳转到该 URL 进行支付
    支付完成后支付宝回调跳转到支付结果页
    """
    # 校验订单归属和状态
    order = get_order_detail(user["user_id"], order_id)
    if order["status"] == "paid":
        raise BusinessError("订单已支付，请勿重复支付")
    if order["status"] == "cancelled":
        raise BusinessError("订单已取消，无法支付")

    try:
        alipay = _get_alipay_client()

        # 动态构造 return_url，包含订单号和来源标记，以便前端检测支付结果
        return_url = ALIPAY_RETURN_URL.replace("__ORDER_ID__", str(order_id))
        notify_url = ALIPAY_NOTIFY_URL

        # 构造支付订单信息
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=str(order_id),
            total_amount=str(order["total_amount"]),
            subject=f"订单 #{order_id}",
            return_url=return_url,
            notify_url=notify_url,
        )

        # 支付宝沙箱网关
        pay_url = f"https://openapi-sandbox.dl.alipaydev.com/gateway.do?{order_string}"
        return {"code": 0, "data": {"pay_url": pay_url}, "message": "success"}
    except BusinessError:
        raise
    except Exception as e:
        raise BusinessError(f"创建支付订单失败：{str(e)}")


@router.get("/alipay/qr-pay/{order_id}")
def alipay_qr_pay(order_id: int, user: dict = Depends(get_current_user)):
    """
    支付宝扫码支付（当面付）
    返回支付宝预下单二维码链接
    注意：必须使用沙箱买家账号登录支付宝扫码
    """
    order = get_order_detail(user["user_id"], order_id)
    if order["status"] == "paid":
        raise BusinessError("订单已支付，请勿重复支付")
    if order["status"] == "cancelled":
        raise BusinessError("订单已取消，无法支付")

    try:
        alipay = _get_alipay_client()

        result = alipay.api_alipay_trade_precreate(
            out_trade_no=str(order_id),
            total_amount=str(order["total_amount"]),
            subject=f"订单 #{order_id}",
        )

        if result.get("code") == "10000":
            qr_code = result.get("qr_code", "")
            return {"code": 0, "data": {"qr_code": qr_code}, "message": "success"}
        else:
            raise BusinessError(f"创建二维码失败：{result.get('sub_msg', result.get('msg', '未知错误'))}")

    except BusinessError:
        raise
    except Exception as e:
        raise BusinessError(f"创建支付订单失败：{str(e)}")


@router.get("/alipay/query/{order_id}")
def alipay_query_pay(order_id: int, user: dict = Depends(get_current_user)):
    """
    主动查询支付宝交易状态
    沙箱环境下异步通知无法到达 localhost，前端轮询时需主动查询支付宝端是否已完成支付
    如果支付宝端交易成功，自动调用 pay_order 更新本地订单状态
    """
    order = get_order_detail(user["user_id"], order_id)

    # 如果本地已支付，直接返回成功
    if order["status"] == "paid":
        return {"code": 0, "data": {"status": "paid", "trade_status": "TRADE_SUCCESS"}, "message": "订单已支付"}

    if order["status"] == "cancelled":
        return {"code": 0, "data": {"status": "cancelled", "trade_status": ""}, "message": "订单已取消"}

    # 本地仍是 pending，主动查询支付宝端交易状态
    try:
        alipay = _get_alipay_client()
        result = alipay.api_alipay_trade_query(out_trade_no=str(order_id))

        trade_status = result.get("trade_status", "")

        # 支付宝端交易成功，更新本地订单
        if trade_status in ("TRADE_SUCCESS", "TRADE_FINISHED"):
            pay_order(user["user_id"], order_id)
            return {"code": 0, "data": {"status": "paid", "trade_status": trade_status}, "message": "支付成功"}

        # 支付宝端交易关闭/退款
        if trade_status in ("TRADE_CLOSED",):
            return {"code": 0, "data": {"status": "closed", "trade_status": trade_status}, "message": "交易已关闭"}

        # 还在等待支付（WAIT_BUYER_PAY）或未查到交易
        return {"code": 0, "data": {"status": "pending", "trade_status": trade_status}, "message": "等待支付"}

    except BusinessError:
        raise
    except Exception as e:
        # 查询失败不影响正常流程，返回当前本地状态
        return {"code": 0, "data": {"status": order["status"], "trade_status": ""}, "message": f"查询支付宝状态失败：{str(e)}"}


@router.post("/alipay/notify")
async def alipay_notify(request: Request):
    """
    支付宝异步通知回调
    支付宝支付成功后，会 POST 通知到这个地址
    注意：沙箱环境下 localhost 无法被支付宝服务器访问，此接口仅在生产环境有效
    """
    import json

    data = await request.form()
    data_dict = dict(data)

    try:
        alipay = _get_alipay_client()
        signature = data_dict.pop("sign", "")
        sign_type = data_dict.pop("sign_type", "RSA2")

        # 验签
        verified = alipay.verify(data_dict, signature)
        if not verified:
            return "failure"

        # 验证交易状态
        trade_status = data_dict.get("trade_status", "")
        if trade_status in ("TRADE_SUCCESS", "TRADE_FINISHED"):
            out_trade_no = data_dict.get("out_trade_no", "")
            order_id = int(out_trade_no)
            # 调用支付逻辑
            from infrastructure.database import get_cursor
            with get_cursor() as cur:
                cur.execute("SELECT user_id FROM shop.orders WHERE id = %s", (order_id,))
                row = cur.fetchone()
                if row:
                    pay_order(row["user_id"], order_id)

        return "success"
    except Exception:
        return "failure"


@router.post("/mock-pay/{order_id}")
def mock_pay(order_id: int, user: dict = Depends(get_current_user)):
    """
    模拟支付（测试用）
    直接调用 pay_order 完成支付，不经过支付宝
    """
    try:
        order = pay_order(user["user_id"], order_id)
        return {"code": 0, "data": order, "message": "支付成功"}
    except (NotFoundError, BusinessError) as e:
        raise
    except Exception as e:
        raise BusinessError(f"支付失败：{str(e)}")
