import zmq
import mnist_pb2
import tensorflow_datasets as tfds
import numpy as np
import time
from concurrent.futures import ThreadPoolExecutor

NODOS_FILLS = ["192.168.98.143", "192.168.98.144"]

print("Cargando MNIST...")
dataset = tfds.load('mnist', split='train', as_supervised=True)
imagenes_brutas = [img.astype(np.float32) for img, label in tfds.as_numpy(dataset)]

# Particionado idéntico
tamano_particion = len(imagenes_brutas) // len(NODOS_FILLS)
datos_preparados = []
bytes_totales = 0

for i, ip in enumerate(NODOS_FILLS):
    inicio = i * tamano_particion
    fin = (i + 1) * tamano_particion if i < (len(NODOS_FILLS)-1) else len(imagenes_brutas)
    particion_np = np.array(imagenes_brutas[inicio:fin])
    
    peticion = mnist_pb2.BatchRequest(
        batch_id=i, 
        image_data=particion_np.tobytes()
    )
    payload_serialized = peticion.SerializeToString()
    
    bytes_totales += len(payload_serialized)
    
    datos_preparados.append((f"tcp://{ip}:8000", payload_serialized))

def enviar_tarea_zmq(config):
    addr, payload_serialized = config
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.setsockopt(zmq.RCVTIMEO, 300000) # 5 min timeout
    try:
        socket.connect(addr)
        socket.send(payload_serialized)
        
        resp_bytes = socket.recv()
        response = mnist_pb2.BatchResponse()
        response.ParseFromString(resp_bytes)
        
        return {
            "ram_mb": response.ram_usage,
            "cpu_percent": response.cpu_usage,
            "imagenes_contadas": response.images_processed
        }
    except Exception as e:
        print(f"Error en {addr}: {e}")
        return {"error": str(e), "addr": addr}
    finally:
        socket.close()
        context.term()

print(f"Lanzando proceso ZeroMQ en {len(NODOS_FILLS)} nodos...")
inicio_t = time.time()

with ThreadPoolExecutor(max_workers=len(NODOS_FILLS)) as executor:
    resultados = list(executor.map(enviar_tarea_zmq, datos_preparados))

fin_t = time.time()

# --- Consolidación ---
tiempo_total = fin_t - inicio_t
exitos = [r for r in resultados if "error" not in r]
tasa_exito = (len(exitos) / len(NODOS_FILLS)) * 100
throughput = len(imagenes_brutas) / tiempo_total
ram_media = sum(r["ram_mb"] for r in exitos) / len(exitos) if exitos else 0
cpu_media = sum(r["cpu_percent"] for r in exitos) / len(exitos) if exitos else 0

# --- Tabla Final ---
print("\n" + "="*50)
print(" RESULTADOS DE LA COMPARATIVA TÉCNICA ")
print("="*50)
print(f"{'Protocolo de Comunicación:':<30} ZeroMQ (Protobuf/Binary)") 
print(f"{'Tiempo Total (s):':<30} {tiempo_total:.2f} s")
print(f"{'Throughput (img/s):':<30} {throughput:.2f} img/s")
print(f"{'RAM Máx. Worker (MB):':<30} {ram_media:.2f} MB")
print(f"{'CPU Promedio (%):':<30} {cpu_media:.2f} %")
print(f"{'Datos Totales Red (MB):':<30} {bytes_totales / (1024*1024):.2f} MB")
print(f"{'Tasa Éxito (%):':<30} {tasa_exito:.2f} %")
print("="*50)