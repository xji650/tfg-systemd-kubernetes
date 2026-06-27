FROM docker.io/library/python:3.11-slim

RUN pip install --upgrade pip

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python -m grpc_tools.protoc -I. --python_out=. mnist.proto

EXPOSE 8000

CMD ["python", "-u", "worker.py"]