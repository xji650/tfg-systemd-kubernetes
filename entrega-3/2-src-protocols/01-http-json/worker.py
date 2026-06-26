from fastapi import FastAPI, Request, UploadFile, File
import uvicorn
import psutil
import os
import time
import torch
import torch.nn as nn
import numpy as np

app = FastAPI()
process = psutil.Process(os.getpid())

# Inicialización obligatoria para psutil
process.cpu_percent(interval=None)

# --- 1. DEFINICIÓN DE LA ARQUITECTURA IA ---
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
        x = x.view(-1, 64 * 7 * 7)
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# Variables globales para la IA
model = None
device = torch.device("cpu") # Los workers edge suelen usar CPU

# --- 2. RUTA PARA RECIBIR EL MODELO DEL MASTER ---
@app.post("/upload_model")
async def upload_model(file: UploadFile = File(...)):
    global model
    # Guardamos el archivo .pth que nos envía el master
    contents = await file.read()
    with open("worker_model.pth", "wb") as f:
        f.write(contents)
    
    # Cargamos el cerebro en la red neuronal
    model = CNN()
    model.load_state_dict(torch.load("worker_model.pth", map_location=device))
    model.eval() # Modo inferencia
    return {"status": "OK", "message": "¡Cerebro IA recibido y cargado en memoria!"}

# --- 3. RUTA DE INFERENCIA (CLASIFICAR IMÁGENES) ---
@app.post("/procesar")
async def procesar_datos(request: Request):
    # 1. Limpieza de buffer de CPU
    process.cpu_percent(interval=None)
    start_proc = time.perf_counter()
    
    # 2. Deserialización
    payload = await request.json()
    imagenes = payload.get("imagenes", [])
    
    predicciones = []
    
    # 3. Trabajo real de la Inteligencia Artificial
    if model is not None and len(imagenes) > 0:
        try:
            # El Master nos envía listas de tamaño (28, 28, 1) con valores de 0 a 255.
            # PyTorch necesita formato Tensor (Batch, Canales, Alto, Ancho) y normalizado.
            imgs_np = np.array(imagenes, dtype=np.float32)
            imgs_np = imgs_np / 255.0 # Escalar de 0 a 1
            imgs_np = (imgs_np - 0.1307) / 0.3081 # Normalizar (media y desviación MNIST)
            
            # Reordenar dimensiones de (N, 28, 28, 1) a (N, 1, 28, 28)
            imgs_tensor = torch.tensor(imgs_np).permute(0, 3, 1, 2)
            
            with torch.no_grad():
                outputs = model(imgs_tensor)
                _, preds = torch.max(outputs, 1)
                predicciones = preds.tolist() # Convertimos el tensor a lista normal
        except Exception as e:
            print(f"Error procesando imágenes: {e}")

    # 4. Medición de recursos (¡Mantenemos tus métricas intactas!)
    ram_mb = process.memory_info().rss / (1024 * 1024)
    cpu_usage = process.cpu_percent(interval=None)
    
    end_proc = time.perf_counter()
    t_proc_ms = (end_proc - start_proc) * 1000
    
    print(f"RAM: {ram_mb:.2f} MB, CPU: {cpu_usage}%, T_proc: {t_proc_ms:.2f} ms")

    return {
        "batch_id": payload.get("batch_id", "N/A"),
        "images_processed": len(imagenes),
        "predictions": predicciones[:5], # Devolvemos solo las 5 primeras predicciones para no saturar la red de vuelta
        "status": "OK",
        "ram_max_mb": ram_mb,
        "cpu_promedio": cpu_usage,
        "t_proc_ms": t_proc_ms
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)