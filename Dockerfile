# 使用官方 Python 基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制 requirements.txt 并安装依赖
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口 5000
EXPOSE 5000

# 使用 Gunicorn 启动 Flask 应用

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "wsgi:appx"]
