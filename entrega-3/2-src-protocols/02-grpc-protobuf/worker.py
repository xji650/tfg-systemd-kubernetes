import os
import time
import psutil
import grpc
from concurrent import futures
import numpy as np

import torch
import torch.nn as nn

import mnist_pb2
import mnist_pb2_grpc

# =====================================================================
# 1. DEFINICIÓN DE LA ARQUITECTURA IA (Debe ser idéntica al Master)
# =====================================================================
class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, stride=1, padding=1)
        self.relu = nn.ReLU()
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.pool(self.relu(self.conv1(x)))
        x = self.pool(self.relu(self.conv2(x)))
        x = x.reshape(-1, 64 * 7 * 7)
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        return x

model = CNN()
MODEL_LOCAL_PATH = "model_local.pth"

# =====================================================================
# 2. SERVIDOR GRPC
# =====================================================================
class MnistServicer(mnist_pb2_grpc.MnistServiceServicer):
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.process.cpu_percent(interval=None)

    def UploadModel(self, request, context):
        print("-> Recibiendo modelo vía gRPC...")
        with open(MODEL_LOCAL_PATH, "wb") as f:
            f.write(request.model_data)
        model.load_state_dict(torch.load(MODEL_LOCAL_PATH))
        model.eval()
        print("-> Modelo IA cargado en RAM.")
        return mnist_pb2.ModelResponse(message="OK")

    def Procesar(self, request, context):
        self.process.cpu_percent(interval=None)
        start_proc = time.perf_counter()
        
        # Deserialización binaria ultra-rápida y pase a PyTorch
        datos = np.frombuffer(request.image_data, dtype=np.float32).copy()
        imagenes_tensor = torch.tensor(datos).view(-1, 1, 28, 28)
        
        # INFERENCIA IA
        with torch.no_grad():
            outputs = model(imagenes_tensor)
            _, predicted = torch.max(outputs.data, 1)
            
        ram_usage = self.process.memory_info().rss / (1024 * 1024)
        cpu_usage = self.process.cpu_percent(interval=None)
        t_proc_ms = (time.perf_counter() - start_proc) * 1000
        
        return mnist_pb2.BatchResponse(
            batch_id=request.batch_id,
            predictions=predicted.tolist(),
            status="OK",
            ram_usage=float(ram_usage),
            cpu_usage=float(cpu_usage),
            t_proc_ms=float(t_proc_ms)
        )

def serve():
    MAX_MESSAGE_LENGTH = 200 * 1024 * 1024 
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
            ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH)
        ]
    )
    mnist_pb2_grpc.add_MnistServiceServicer_to_server(MnistServicer(), server)
    server.add_insecure_port('[::]:8000') 
    print("Iniciando Worker Edge IA (gRPC/Protobuf) en puerto 8000...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()