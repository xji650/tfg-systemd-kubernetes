FROM docker.io/library/python:3.11-slim

WORKDIR /app

RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Solo copiamos el worker, ya no existe mnist.proto
COPY worker.py .

EXPOSE 8000

CMD ["python3", "-u", "worker.py"]