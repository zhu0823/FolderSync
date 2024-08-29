# 使用官方的 Python 镜像作为基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制当前目录内容到工作目录
COPY . .

# 安装依赖项
RUN pip install -r requirements.txt

# 暴露端口
EXPOSE 18000

# 挂载目录
VOLUME [ "/data", "/logs" ]

# 启动服务
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "18000"]