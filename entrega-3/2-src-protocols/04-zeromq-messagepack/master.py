import os
import time
import random
import zmq
import numpy as np
import msgpack
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
ASSETS_DIR = "assets"
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
        return

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
    
    print("-> Entrenando modelo...")
    inicio_entrenamiento = time.perf_counter()
    model.train()
    
    for inputs, labels in train_loader:
        optimizer.zero_grad()
        loss = criterion(model(inputs), labels)
        loss.backward()
        optimizer.step()
        train_losses.append(loss.item())
        
    tiempo_entrenamiento = time.perf_counter() - inicio_entrenamiento
    torch.save(model.state_dict(), MODEL_PATH)
    tamano_mb = os.path.getsize(MODEL_PATH) / (1024 * 1024)
    
    # --- FASE DE EVALUACIÓN (MÉTRICAS IA) ---
    print("-> Evaluando modelo...")
    model.eval()
    correct, total = 0, 0
    all_preds, all_labels = [], []

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
    plt.savefig(os.path.join(ASSETS_DIR, 'loss-curve.png'))
    plt.close()
    
    cm = confusion_matrix(all_labels, all_preds)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('Matriz de Confusión - Validación')
    plt.xlabel('Predicción de la IA')
    plt.ylabel('Valor Real')
    plt.savefig(os.path.join(ASSETS_DIR, 'matriz-confusion.png'))
    plt.close()
    
    print("\n--- MÉTRICAS DEL MODELO (IA) ---")
    print(f"Precisión Validación:           {val_accuracy:.2f}%")
    print(f"Tiempo de entrenamiento:        {tiempo_entrenamiento:.2f} s")
    print(f"Peso del artefacto (.pth):      {tamano_mb:.2f} MB")
    print(f"-> Gráficas generadas y guardadas en la carpeta '{ASSETS_DIR}/'.\n")

# =====================================================================
# 3. EL MASTER COMO ORQUESTADOR (Despliegue)
# =====================================================================    
def distribuir_modelo():
    print("\n" + "="*50)
    print("2. DISTRIBUYENDO EL MODELO VÍA ZEROMQ + MSGPACK")
    print("="*50)
    
    with open(MODEL_PATH, "rb") as f:
        model_bytes = f.read()
        
    peticion = {'model_data': model_bytes}
    payload_serialized = msgpack.packb(peticion, use_bin_type=True)
    
    for ip in NODOS_FILLS:
        addr = f"tcp://{ip}:8000"
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.setsockopt(zmq.RCVTIMEO, 5000)
        try:
            socket.connect(addr)
            # Enviamos el multipart indicando que es un UPLOAD
            socket.send_multipart([b"UPLOAD", payload_serialized])
            
            resp_bytes = socket.recv()
            res = msgpack.unpackb(resp_bytes, raw=False)
            print(f"Worker [{addr}] respondió: {res.get('message', 'Sin mensaje')}")
        except Exception as e:
            print(f"Error en Worker [{addr}]: {e}")
        finally:
            socket.close()
            context.term()

def enviar_tarea_zmq(config):
    addr, payload_serialized, payload_size = config
    
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.setsockopt(zmq.RCVTIMEO, 300000) 
    
    inicio_rtt = time.perf_counter() 
    try:
        socket.connect(addr)
        # Enviamos el multipart indicando que es una INFERENCIA
        socket.send_multipart([b"INFER", payload_serialized])
        
        resp_bytes = socket.recv()
        fin_rtt = time.perf_counter()
        
        # Deserializar límite amplio
        response = msgpack.unpackb(resp_bytes, raw=False, max_bin_len=200*1024*1024)
        
        if response.get('status') == 'ERROR':
            return {"error": response.get('error'), "addr": addr}
            
        return {
            "addr": addr,
            "ram_max_mb": response['ram_usage'],
            "cpu_promedio": response['cpu_usage'],
            "t_proc_ms": response['t_proc_ms'],
            "predictions": response['predictions'],
            "rtt_ms": (fin_rtt - inicio_rtt) * 1000,
            "payload_bytes": payload_size
        }
    except Exception as e:
        return {"error": str(e), "addr": addr}
    finally:
        socket.close()
        context.term()

# =====================================================================
# 4. BENCHMARK DE RENDIMIENTO (RED)
# =====================================================================
if __name__ == "__main__":
    entrenar_y_evaluar_modelo()
    distribuir_modelo()
    
    print("\n" + "="*50)
    print("3. INICIANDO BENCHMARK DE INFERENCIA (RED ZEROMQ + MSGPACK)")
    print("="*50)
    
    transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])
    test_dataset = torchvision.datasets.MNIST(root='./data', train=False, download=True, transform=transform)
    
    lista_imagenes = []
    lista_etiquetas = []

    for i in range(2000):
        img_tensor, label = test_dataset[i]
        lista_imagenes.append(img_tensor.squeeze().tolist())
        lista_etiquetas.append(label)

    tamano_particion = len(lista_imagenes) // len(NODOS_FILLS)
    datos_preparados = []
    
    for i, ip in enumerate(NODOS_FILLS):
        inicio = i * tamano_particion
        fin = (i + 1) * tamano_particion if i < (len(NODOS_FILLS)-1) else len(lista_imagenes)
        
        particion_np = np.array(lista_imagenes[inicio:fin], dtype=np.float32)
        
        # Empaquetamos como diccionario
        peticion = {
            'batch_id': i, 
            'image_data': particion_np.tobytes()
        }
        payload_serialized = msgpack.packb(peticion, use_bin_type=True)
        
        addr = f"tcp://{ip}:8000"
        datos_preparados.append((addr, payload_serialized, len(payload_serialized)))

    tiempo_inicio_total = time.perf_counter()
    with ThreadPoolExecutor(max_workers=len(NODOS_FILLS)) as executor:
        resultados = list(executor.map(enviar_tarea_zmq, datos_preparados))
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
        
        try:
            total_imgs = len(exitos[0]["predictions"])
            indices = random.sample(range(total_imgs), 10)
            fig, axes = plt.subplots(2, 5, figsize=(12, 5))
            fig.suptitle(f"10 Ejemplos Aleatorios (ZMQ+MsgPack) - Worker [{exitos[0]['addr']}]", fontsize=16)
            for idx, ax in enumerate(axes.flat):
                i = indices[idx]
                img_array = np.array(lista_imagenes[i]).reshape(28, 28)
                ax.imshow(img_array, cmap='gray')
                pred, real = exitos[0]["predictions"][i], lista_etiquetas[i]
                ax.set_title(f"Pred: {pred}\nReal: {real}", color="green" if pred == real else "red")
                ax.axis('off')
            plt.tight_layout()
            plt.savefig(os.path.join(ASSETS_DIR, 'ejemplos-predicciones-msgpack.png'), bbox_inches='tight')
            plt.close()
        except Exception as e:
            print(f"Error visual: {e}")
    else:
        ram_pico_max = cpu_media = rtt_medio = t_proc_medio = payload_total_mb = payload_promedio_nodo = 0

    # --- IMPRESIÓN DE LA TABLA FINAL DE RED ---
    print("\n" + "="*50)
    print(" RESULTADOS DE LA COMPARATIVA TÉCNICA (ZeroMQ + MessagePack) ")
    print("="*50)
    print(f"{'Protocolo de Comunicación:':<30} ZeroMQ (MessagePack)")
    print(f"{'Tiempo Total (s):':<30} {tiempo_total:.2f} s")
    print(f"{'Throughput (img/s):':<30} {throughput:.2f}")
    print(f"{'Tasa de Éxito (%):':<30} {tasa_exito:.1f} %")
    print(f"{'Latencia RTT Promedio (ms):':<30} {rtt_medio:.2f} ms")
    print(f"{'Tiempo T_proc Promedio (ms):':<30} {t_proc_medio:.2f} ms")
    print(f"{'Pico Máx. RAM Worker (MB):':<30} {ram_pico_max:.2f} MB")
    print(f"{'CPU Promedio (%):':<30} {cpu_media:.2f} %")
    print(f"{'Payload Promedio por Nodo (MB):':<30} {payload_promedio_nodo:.2f} MB")
    print("="*50)