import os
import time
import psutil
import zmq
import numpy as np
import torch
import torch.nn as nn
import mnist_pb2

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
# 2. SERVIDOR ZEROMQ + PROTOBUF
# =====================================================================
def serve():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:8000")
    
    process = psutil.Process(os.getpid())
    process.cpu_percent(interval=None) 
    
    print("Iniciando Worker Edge IA (ZeroMQ/Protobuf) en puerto 8000...")

    while True:
        # Recibir mensaje multiparte: [TIPO_MENSAJE, PAYLOAD_PROTOBUF]
        frames = socket.recv_multipart()
        comando = frames[0]
        payload_bytes = frames[1]
        
        if comando == b"UPLOAD":
            # Fase 1: Recibir el Modelo
            print("-> Recibiendo modelo vía ZeroMQ...")
            request = mnist_pb2.ModelRequest()
            request.ParseFromString(payload_bytes)
            
            with open(MODEL_LOCAL_PATH, "wb") as f:
                f.write(request.model_data)
                
            model.load_state_dict(torch.load(MODEL_LOCAL_PATH))
            model.eval()
            print("-> Modelo IA cargado en RAM.")
            
            response = mnist_pb2.ModelResponse(message="OK - Modelo cargado")
            socket.send(response.SerializeToString())
            
        elif comando == b"INFER":
            # Fase 2: Inferencia de Imágenes
            process.cpu_percent(interval=None)
            start_proc = time.perf_counter()
            
            request = mnist_pb2.BatchRequest()
            request.ParseFromString(payload_bytes)
            
            # Deserialización binaria y pase a PyTorch
            datos = np.frombuffer(request.image_data, dtype=np.float32).copy()
            cantidad = len(datos) // 784
            imagenes_tensor = torch.tensor(datos).view(-1, 1, 28, 28)
            
            with torch.no_grad():
                outputs = model(imagenes_tensor)
                _, predicted = torch.max(outputs.data, 1)
                
            ram_usage = process.memory_info().rss / (1024 * 1024)
            cpu_usage = process.cpu_percent(interval=None)
            
            end_proc = time.perf_counter()
            t_proc_ms = (end_proc - start_proc) * 1000
            
            response = mnist_pb2.BatchResponse(
                batch_id=request.batch_id,
                predictions=predicted.tolist(),
                status="OK",
                ram_usage=float(ram_usage),
                cpu_usage=float(cpu_usage),
                t_proc_ms=float(t_proc_ms)
            )
            socket.send(response.SerializeToString())

            print(f"ZMQ: Procesadas {int(cantidad)} img. RAM: {ram_usage:.2f}MB, CPU: {cpu_usage}%, T_proc: {t_proc_ms:.2f}ms")

if __name__ == "__main__":
    serve()