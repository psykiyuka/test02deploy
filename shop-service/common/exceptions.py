class ShopException(Exception):
    code = 50000
    message = "内部服务器错误"
    http_status = 500

    def __init__(self, message: str = None, code: int = None):
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code
        super().__init__(self.message)


class ValidationError(ShopException):
    code = 40001
    message = "参数校验失败"
    http_status = 400


class AuthenticationError(ShopException):
    code = 40101
    message = "未登录或Token过期"
    http_status = 401


class PermissionDeniedError(ShopException):
    code = 40301
    message = "无操作权限"
    http_status = 403


class NotFoundError(ShopException):
    code = 40401
    message = "资源不存在"
    http_status = 404


class BusinessError(ShopException):
    code = 42201
    message = "业务规则冲突"
    http_status = 422


class DatabaseError(ShopException):
    code = 50001
    message = "数据库异常"
    http_status = 500


class InternalError(ShopException):
    code = 50002
    message = "未预期的内部错误"
    http_status = 500