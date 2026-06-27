import os
import time
import shutil
import psutil
from fastapi import FastAPI, UploadFile, File, Request
import uvicorn

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
        x = x.reshape(-1, 64 * 7 * 7) # Aplanamos el tensor
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# =====================================================================
# 2. INICIALIZACIÓN DEL ENTORNO Y SERVIDOR
# =====================================================================
app = FastAPI()
process = psutil.Process(os.getpid())
process.cpu_percent(interval=None) # Inicialización del monitor de CPU

# Instanciamos el modelo vacío globalmente
model = CNN()
MODEL_LOCAL_PATH = "model_local.pth"

# =====================================================================
# 3. ENDPOINTS DE LA API (Despliegue e Inferencia)
# =====================================================================

@app.post("/upload_model")
async def upload_model(file: UploadFile = File(...)):
    """ Recibe el modelo del Master y lo carga en memoria """
    print(f"-> Recibiendo modelo: {file.filename}")
    
    # 1. Guardar el archivo físicamente
    with open(MODEL_LOCAL_PATH, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 2. Cargar los "conocimientos" en la red neuronal
    model.load_state_dict(torch.load(MODEL_LOCAL_PATH))
    model.eval() # Ponemos el modelo en modo inferencia (MUY IMPORTANTE)
    
    print("-> Modelo cargado en RAM y listo para inferencias.")
    return {"message": "Modelo recibido y cargado con éxito"}

@app.post("/procesar")
async def procesar_datos(request: Request):
    """ Recibe imágenes, hace inferencia y mide el rendimiento """
    
    # Limpiamos el buffer de CPU para medir solo este ciclo
    process.cpu_percent(interval=None)
    start_proc = time.perf_counter()
    
    # 1. Recepción y Deserialización
    payload = await request.json()
    imagenes_lista = payload.get("imagenes", [])
    
    # Transformar los datos a Tensores de PyTorch. 
    # Aseguramos la forma [Batch, Canales, Alto, Ancho] -> [-1, 1, 28, 28]
    imagenes_tensor = torch.tensor(imagenes_lista, dtype=torch.float32).view(-1, 1, 28, 28)
    
    # 2. INFERENCIA
    with torch.no_grad(): # Apaga el cálculo de gradientes (ahorra mucha RAM/CPU)
        outputs = model(imagenes_tensor)
        _, predicted = torch.max(outputs.data, 1)
        
    predicciones = predicted.tolist()
    
    # 3. Medición de Recursos (Justo después del esfuerzo computacional)
    ram_mb = process.memory_info().rss / (1024 * 1024)
    cpu_usage = process.cpu_percent(interval=None)
    
    end_proc = time.perf_counter()
    t_proc_ms = (end_proc - start_proc) * 1000
    
    return {
        "status": "OK",
        "predictions": predicciones,
        "ram_usage": float(ram_mb),
        "cpu_usage": float(cpu_usage),
        "t_proc_ms": float(t_proc_ms)
    }

if __name__ == "__main__":
    print("Iniciando Worker Edge (HTTP/REST)...")
    uvicorn.run(app, host="0.0.0.0", port=8000)