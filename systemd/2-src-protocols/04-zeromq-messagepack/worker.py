import os
import time
import psutil
import zmq
import numpy as np
import msgpack
import torch
import torch.nn as nn

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
# 2. SERVIDOR ZEROMQ + MSGPACK
# =====================================================================
def serve():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:8000")
    
    process = psutil.Process(os.getpid())
    process.cpu_percent(interval=None) 
    
    print("Iniciando Worker Edge IA (ZeroMQ + MessagePack) en puerto 8000...")

    while True:
        try:
            # Recibir mensaje multiparte: [COMANDO, PAYLOAD_MSGPACK]
            frames = socket.recv_multipart()
            comando = frames[0]
            
            # Deserializar con límite amplio de 200MB
            data = msgpack.unpackb(frames[1], raw=False, max_bin_len=200*1024*1024)
            
            if comando == b"UPLOAD":
                print("-> Recibiendo modelo vía ZeroMQ (MsgPack)...")
                with open(MODEL_LOCAL_PATH, "wb") as f:
                    f.write(data['model_data'])
                    
                model.load_state_dict(torch.load(MODEL_LOCAL_PATH))
                model.eval()
                print("-> Modelo IA cargado en RAM.")
                
                response = {'status': 'OK', 'message': 'Modelo cargado'}
                socket.send(msgpack.packb(response, use_bin_type=True))
                
            elif comando == b"INFER":
                process.cpu_percent(interval=None)
                start_proc = time.perf_counter()
                
                # Inferencia IA
                datos_np = np.frombuffer(data['image_data'], dtype=np.float32).copy()
                cantidad = len(datos_np) // 784
                imagenes_tensor = torch.tensor(datos_np).view(-1, 1, 28, 28)
                
                with torch.no_grad():
                    outputs = model(imagenes_tensor)
                    _, predicted = torch.max(outputs.data, 1)
                    
                ram_usage = process.memory_info().rss / (1024 * 1024)
                cpu_usage = process.cpu_percent(interval=None)
                
                end_proc = time.perf_counter()
                t_proc_ms = (end_proc - start_proc) * 1000
                
                # Respuesta como Diccionario
                response = {
                    'batch_id': data['batch_id'],
                    'predictions': predicted.tolist(),
                    'status': 'OK',
                    'ram_usage': float(ram_usage),
                    'cpu_usage': float(cpu_usage),
                    't_proc_ms': float(t_proc_ms)
                }
                socket.send(msgpack.packb(response, use_bin_type=True))

        except Exception as e:
            print(f"Error procesando petición: {e}")
            error_resp = {'status': 'ERROR', 'error': str(e)}
            socket.send(msgpack.packb(error_resp, use_bin_type=True))

if __name__ == "__main__":
    serve()