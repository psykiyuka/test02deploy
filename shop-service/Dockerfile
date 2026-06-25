FROM python:3.10.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 开发模式：代码通过 volume 挂载，无需每次重建镜像
# 启动 uvicorn 并开启 --reload 自动热重载
COPY . .

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
