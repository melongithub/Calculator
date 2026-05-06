FROM python:3.10-alpine
WORKDIR /app
# 将依赖文件复制进去并安装（这一步会利用你的虚拟内存）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# 把所有代码复制进去
COPY . .
# 运行后端程序
CMD ["python", "app.py"]
