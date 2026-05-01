FROM docker.io/library/python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY mnist.proto .
COPY worker.py .
RUN python -m grpc_tools.protoc -I. --python_out=. mnist.proto
EXPOSE 8000
CMD ["python", "-u", "worker.py"]