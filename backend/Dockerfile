FROM python:3.10-slim

# 创建应用用户，UID可通过构建参数传入
ARG APP_UID=1000
ARG APP_GID=1000

RUN groupadd -g ${APP_GID} appuser && \
    useradd -u ${APP_UID} -g appuser -m -s /bin/bash appuser

WORKDIR /app

# 更换为国内镜像源(阿里云)
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制twork核心库(运行时通过PYTHONPATH引入,不安装)
COPY twork ./twork

# 复制requirements
COPY backend/requirements.txt .

# 配置pip国内镜像源并安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY backend/app/ ./app/
COPY backend/scripts/ ./scripts/

# 创建必要的目录并设置权限
RUN mkdir -p /app/data/uploads /app/data/outputs /app/data/db /app/logs && \
    chown -R appuser:appuser /app

# 设置环境变量,将twork添加到Python路径
ENV PYTHONPATH="/app:${PYTHONPATH}"

# 切换到非root用户
USER appuser

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
