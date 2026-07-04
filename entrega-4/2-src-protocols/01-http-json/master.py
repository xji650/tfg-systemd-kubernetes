import os
import time
import json
import random
import requests
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
from concurrent.futures import ThreadPoolExecutor

import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader, random_split

# =====================================================================
# CONFIGURACIÓN DEL ENTORNO
# =====================================================================
NODOS_FILLS = ["192.168.98.143", "192.168.98.144"]
MODEL_PATH = "best_model.pth"
ASSETS_DIR = "assets" # Definimos la carpeta de destino

# Creamos la carpeta automáticamente si no existe
os.makedirs(ASSETS_DIR, exist_ok=True)

# =====================================================================
# 1. DEFINICIÓN DE LA ARQUITECTURA IA
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

# =====================================================================
# 2. EL MASTER COMO CIENTÍFICO DE DATOS (Benchmark IA)
# =====================================================================
def entrenar_y_evaluar_modelo():
    print("\n" + "="*50)
    print("1. EVALUACIÓN Y ENTRENAMIENTO DEL MODELO IA")
    print("="*50)
    
    transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])
    
    if os.path.exists(MODEL_PATH):
        print(f"-> Archivo '{MODEL_PATH}' encontrado en caché.")
        print("-> Saltando fase de entrenamiento para aislar métricas de red.\n")
        return

    print("-> Descargando y preparando dataset MNIST (80% Train / 20% Val)...")
    full_train = torchvision.datasets.MNIST(root='./data', train=True, download=True, transform=transform)
    
    train_size = int(0.8 * len(full_train))
    val_size = len(full_train) - train_size
    train_dataset, val_dataset = random_split(full_train, [train_size, val_size])
    
    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False)
    
    model = CNN()
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)
    
    train_losses = []
    
    # --- FASE DE ENTRENAMIENTO ---
    print("-> Entrenando modelo (1 Época)...")
    inicio_entrenamiento = time.perf_counter()
    model.train()
    
    for inputs, labels in train_loader:
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        train_losses.append(loss.item())
        
    tiempo_entrenamiento = time.perf_counter() - inicio_entrenamiento
    torch.save(model.state_dict(), MODEL_PATH)
    tamano_mb = os.path.getsize(MODEL_PATH) / (1024 * 1024)
    
    # --- FASE DE EVALUACIÓN (MÉTRICAS IA) ---
    print("-> Evaluando modelo con datos de validación...")
    model.eval()
    correct = 0
    total = 0
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for inputs, labels in val_loader:
            outputs = model(inputs)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            all_preds.extend(predicted.tolist())
            all_labels.extend(labels.tolist())
            
    val_accuracy = 100 * correct / total
    
    # --- ARTEFACTOS VISUALES IA ---
    plt.figure(figsize=(8, 5))
    plt.plot(train_losses, color='blue', label='Train Loss')
    plt.title('Curva de Aprendizaje (1 Época)')
    plt.xlabel('Batches')
    plt.ylabel('Pérdida (Cross Entropy)')
    plt.legend()
    plt.savefig(os.path.join(ASSETS_DIR, 'loss-curve.png')) # Guardado en assets/
    plt.close()
    
    cm = confusion_matrix(all_labels, all_preds)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('Matriz de Confusión - Validación')
    plt.xlabel('Predicción de la IA')
    plt.ylabel('Valor Real')
    plt.savefig(os.path.join(ASSETS_DIR, 'matriz-confusion.png')) # Guardado en assets/
    plt.close()

    print("\n--- MÉTRICAS DEL MODELO (IA) ---")
    print(f"Precisión (Validation Accuracy): {val_accuracy:.2f}%")
    print(f"Tiempo de entrenamiento:         {tiempo_entrenamiento:.2f} s")
    print(f"Peso del artefacto (.pth):       {tamano_mb:.2f} MB")
    print(f"-> Gráficas generadas y guardadas en la carpeta '{ASSETS_DIR}/'.\n")

# =====================================================================
# 3. EL MASTER COMO ORQUESTADOR (Despliegue)
# =====================================================================
def distribuir_modelo():
    print("="*50)
    print("2. DISTRIBUYENDO EL MODELO A LOS WORKERS EDGE")
    print("="*50)
    for ip in NODOS_FILLS:
        try:
            with open(MODEL_PATH, 'rb') as f:
                res = requests.post(f"http://{ip}:30000/upload_model", files={"file": f}, timeout=15)
                print(f"Worker [{ip}] respondió: {res.json().get('message', 'OK')}")
        except Exception as e:
            print(f"Error enviando modelo al Worker [{ip}]: {e}")
    print("\n")

def enviar_tarea(config):
    ip, payload_dict = config
    payload_str = json.dumps(payload_dict)
    payload_bytes = len(payload_str.encode('utf-8'))
    
    inicio_rtt = time.perf_counter() 
    try:
        res = requests.post(f"http://{ip}:30000/procesar", data=payload_str, 
                            headers={'Content-Type': 'application/json'}, timeout=300)
        fin_rtt = time.perf_counter()
        
        datos_worker = res.json()
        return {
            "ip_nodo": ip,
            "ram_max_mb": datos_worker.get('ram_usage', 0),
            "cpu_promedio": datos_worker.get('cpu_usage', 0),
            "t_proc_ms": datos_worker.get('t_proc_ms', 0),
            "predictions": datos_worker.get('predictions', []),
            "rtt_ms": (fin_rtt - inicio_rtt) * 1000,
            "payload_bytes": payload_bytes
        }
    except Exception as e:
        return {"error": str(e), "ip_nodo": ip}

# =====================================================================
# 4. BENCHMARK DE RENDIMIENTO (RED)
# =====================================================================
if __name__ == "__main__":
    entrenar_y_evaluar_modelo()
    distribuir_modelo()
    
    print("="*50)
    print("3. INICIANDO BENCHMARK DE INFERENCIA (RED HTTP)")
    print("="*50)
    print("-> Cargando dataset MNIST de pruebas (vía PyTorch)...")
    
    # Usamos PyTorch para extraer datos normalizados
    transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])
    test_dataset = torchvision.datasets.MNIST(root='./data', train=False, download=True, transform=transform)
    
    lista_imagenes = []
    lista_etiquetas = []
    
    for i in range(2000):
        img_tensor, label = test_dataset[i]
        # Convertimos a lista 2D (28x28) para el JSON
        lista_imagenes.append(img_tensor.squeeze().tolist())
        lista_etiquetas.append(label)

    # Particionamiento de datos para los Workers
    tamano_particion = len(lista_imagenes) // len(NODOS_FILLS)
    datos_preparados = []
    for i, ip in enumerate(NODOS_FILLS):
        inicio = i * tamano_particion
        fin = (i + 1) * tamano_particion if i < (len(NODOS_FILLS)-1) else len(lista_imagenes)
        particion = lista_imagenes[inicio:fin]
        datos_preparados.append((ip, {"imagenes": particion}))

    print(f"-> Lanzando inferencia distribuida en {len(NODOS_FILLS)} nodos Edge...")
    tiempo_inicio_total = time.perf_counter()
    
    with ThreadPoolExecutor(max_workers=len(NODOS_FILLS)) as executor:
        resultados = list(executor.map(enviar_tarea, datos_preparados))
        
    tiempo_total = time.perf_counter() - tiempo_inicio_total
    
    # --- CONSOLIDACIÓN DE RESULTADOS ---
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
        
        # --- GENERAR MOSAICO DE 10 EJEMPLOS VISUALES ---
        try:
            # Obtenemos la cantidad de imágenes que procesó este Worker
            total_imgs_worker = len(exitos[0]["predictions"])
            # Extraemos las etiquetas reales que le correspondían a este Worker (las primeras)
            etiquetas_worker_0 = lista_etiquetas[0:total_imgs_worker]
            
            # Elegimos 10 posiciones al azar
            indices_azar = random.sample(range(total_imgs_worker), 10)
            
            # Extraemos esas 10 posiciones exactas de las listas
            pred_azar = [exitos[0]["predictions"][i] for i in indices_azar]
            img_azar = [datos_preparados[0][1]["imagenes"][i] for i in indices_azar]
            etiq_azar = [etiquetas_worker_0[i] for i in indices_azar]
            
            fig, axes = plt.subplots(2, 5, figsize=(12, 5))
            fig.suptitle(f"10 Ejemplos Aleatorios de Inferencia - Worker [{exitos[0]['ip_nodo']}]", fontsize=16)
            
            for i, ax in enumerate(axes.flat):
                img_array = np.array(img_azar[i]).reshape(28, 28)
                ax.imshow(img_array, cmap='gray')
                ax.set_title(f"Predicción: {pred_azar[i]}\nReal: {etiq_azar[i]}", 
                             color="green" if pred_azar[i] == etiq_azar[i] else "red")
                ax.axis('off')
                
            plt.tight_layout()
            plt.savefig(os.path.join(ASSETS_DIR, 'ejemplos-predicciones-http.png'), bbox_inches='tight')
            plt.close()
            print(f"\n-> Mosaico '10_ejemplos_predicciones.png' generado con imágenes aleatorias.")
        except Exception as e:
            print(f"\nError generando el mosaico de imágenes: {e}")
    else:
        ram_pico_max = cpu_media = rtt_medio = t_proc_medio = payload_total_mb = payload_promedio_nodo = 0

    # --- IMPRESIÓN DE LA TABLA FINAL DE RED ---
    print("\n" + "="*50)
    print(" RESULTADOS DE LA COMPARATIVA TÉCNICA (RED/SYS) ")
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
    print("="*50)