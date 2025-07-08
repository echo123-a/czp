# 构建阶段
FROM python:3.9-slim as builder

# 安装构建依赖
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# 生产阶段
FROM python:3.9-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:${PATH}"

# 从构建阶段复制已安装的包
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app/requirements.txt .

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# 复制项目代码
COPY . .

# 收集静态文件
RUN python manage.py collectstatic --noinput

# 暴露端口
EXPOSE 8000

# 启动 Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "internship_system.wsgi:application"]