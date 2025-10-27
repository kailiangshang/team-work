FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

# 复制测试代码和数据
COPY . .

# 设置Python路径，使其能找到twork模块
ENV PYTHONPATH=/app:/app/../..

# 默认命令
CMD ["python", "test.py"]
