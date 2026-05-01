FROM docker.io/library/python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY worker.py .
COPY mnist.proto .

RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. mnist.proto

EXPOSE 8000

CMD ["python", "-u", "worker.py"] 
