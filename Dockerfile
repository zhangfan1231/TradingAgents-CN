# 使用官方的Python 3.11镜像作为基础镜像
FROM python:3.11
# 设置工作目录
WORKDIR /app
# 将当前目录内容复制到容器的/app目录下
COPY . /app
# 安装任何需要的包
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements_db.txt
# 对外暴露的端口号
EXPOSE 8501
# 运行命令
CMD ["python", "web/app.py"]
