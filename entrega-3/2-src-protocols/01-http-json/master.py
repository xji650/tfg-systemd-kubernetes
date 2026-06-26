import tensorflow_datasets as tfds
import requests
import time
import json
from concurrent.futures import ThreadPoolExecutor
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader

# Configuración del entorno
NODOS_FILLS = ["192.168.98.143", "192.168.98.144"]

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

def entrenar_modelo():
    print("="*50)
    print("1. ENTRENANDO CEREBRO IA EN EL MASTER")
    print("="*50)
    transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])
    train_dataset = torchvision.datasets.MNIST(root='./data', train=True, download=True, transform=transform)
    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
    
    model = CNN()
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)
    
    model.train()
    # Entrenamos solo 1 época para que el benchmark no tarde demasiado
    for inputs, labels in train_loader:
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
    torch.save(model.state_dict(), 'master_model.pth')
    print("-> Entrenamiento completado. Archivo 'master_model.pth' generado.\n")

def distribuir_modelo():
    print("="*50)
    print("2. DISTRIBUYENDO EL MODELO A LOS WORKERS EDGE")
    print("="*50)
    for ip in NODOS_FILLS:
        try:
            with open('master_model.pth', 'rb') as f:
                res = requests.post(f"http://{ip}:8000/upload_model", files={"file": f}, timeout=10)
                print(f"Worker [{ip}] respondió: {res.json()['message']}")
        except Exception as e:
            print(f"Error enviando modelo al Worker [{ip}]: {e}")
    print("\n")

# --- 3. FUNCIONES DE BENCHMARKING (TUS MÉTRICAS) ---
def enviar_tarea(config):
    ip, payload_dict = config
    
    # Serializamos ANTES del RTT para medir el payload real
    payload_str = json.dumps(payload_dict)
    payload_bytes = len(payload_str.encode('utf-8'))
    
    inicio_rtt = time.perf_counter() 
    try:
        res = requests.post(f"http://{ip}:8000/procesar", data=payload_str, headers={'Content-Type': 'application/json'})
        fin_rtt = time.perf_counter()
        
        data = res.json()
        data["rtt_ms"] = (fin_rtt - inicio_rtt) * 1000
        data["payload_bytes"] = payload_bytes
        data["ip_nodo"] = ip
        return data
    except Exception as e:
        return {"error": str(e), "ip_nodo": ip}

if __name__ == "__main__":
    # PASO 1: Entrenar el modelo
    entrenar_modelo()
    
    # PASO 2: Distribuir el modelo por red a los workers
    distribuir_modelo()
    
    # PASO 3: Preparar las imágenes de prueba (Benchmark)
    print("="*50)
    print("3. INICIANDO FASE DE INFERENCIA DISTRIBUIDA")
    print("="*50)
    print("Cargando dataset MNIST de pruebas...")
    dataset = tfds.load('mnist', split='test', as_supervised=True)
    imagenes_brutas = list(tfds.as_numpy(dataset))
    lista_imagenes = [img.tolist() for img, label in imagenes_brutas[:2000]] # Usamos 2000 imágenes para el benchmark
    
    tamano_particion = len(lista_imagenes) // len(NODOS_FILLS)
    datos_preparados = []
    
    for i, ip in enumerate(NODOS_FILLS):
        inicio = i * tamano_particion
        fin = (i + 1) * tamano_particion if i < (len(NODOS_FILLS)-1) else len(lista_imagenes)
        particion = lista_imagenes[inicio:fin]
        datos_preparados.append((ip, {"imagenes": particion}))

    # PASO 4: Lanzar el benchmark con hilos concurrentes
    print("Iniciando envío de lotes de imágenes...")
    tiempo_inicio_total = time.perf_counter()
    
    with ThreadPoolExecutor(max_workers=len(NODOS_FILLS)) as executor:
        resultados = list(executor.map(enviar_tarea, datos_preparados))
        
    tiempo_total = time.perf_counter() - tiempo_inicio_total
    
    # PASO 5: Cálculo de tus Métricas
    exitos = [r for r in resultados if "error" not in r]
    tasa_exito = (len(exitos) / len(NODOS_FILLS)) * 100
    throughput = len(lista_imagenes) / tiempo_total
    
    if exitos:
        ram_pico_max = max(r["ram_max_mb"] for r in exitos) 
        cpu_media = sum(r["cpu_promedio"] for r in exitos) / len(exitos)
        rtt_medio = sum(r["rtt_ms"] for r in exitos) / len(exitos)
        t_proc_medio = sum(r["t_proc_ms"] for r in exitos) / len(exitos)
        payload_total_mb = sum(r["payload_bytes"] for r in exitos) / (1024 * 1024)
        payload_promedio_nodo = payload_total_mb / len(exitos)
        
        # Imprimir una prueba de que la IA funcionó
        print("\n[Muestra de Predicciones del Worker 1]:", exitos[0].get("predictions", []))
    else:
        ram_pico_max = cpu_media = rtt_medio = t_proc_medio = payload_total_mb = payload_promedio_nodo = 0

    # --- Impresión de la Tabla Final (Igual que en tu archivo original) ---
    print("\n" + "="*50)
    print(" RESULTADOS DE LA COMPARATIVA TÉCNICA (IA) ")
    print("="*50)
    print(f"{'Protocolo de Comunicación:':<30} HTTP/REST (JSON)")
    print(f"{'Tiempo Total (s):':<30} {tiempo_total:.2f} s")
    print(f"{'Throughput (img/s):':<30} {throughput:.2f}")
    print(f"{'Tasa de Éxito (%):':<30} {tasa_exito:.1f} %")
    print(f"{'Latencia RTT Promedio (ms):':<30} {rtt_medio:.2f} ms")
    print(f"{'Tiempo T_proc Promedio (ms):':<30} {t_proc_medio:.2f} ms")
    print(f"{'Pico Máx. RAM Worker (MB):':<30} {ram_pico_max:.2f} MB")
    print(f"{'CPU Promedio (%):':<30} {cpu_media:.2f} %")
    print(f"{'Payload Promedio por Nodo (MB):':<30} {payload_promedio_nodo:.2f} MB")