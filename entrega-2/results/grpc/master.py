import grpc
import mnist_pb2
import mnist_pb2_grpc
import tensorflow_datasets as tfds
import numpy as np
import time
from concurrent.futures import ThreadPoolExecutor

NODOS_FILLS = ["192.168.98.143:8000", "192.168.98.144:8000"]

print("Cargando MNIST...")
dataset = tfds.load('mnist', split='train', as_supervised=True)
# Cargamos como float32 para gRPC
imagenes_brutas = [img.astype(np.float32) for img, label in tfds.as_numpy(dataset)]

# Preparación de particiones
tamano_particion = len(imagenes_brutas) // len(NODOS_FILLS)
datos_preparados = []

for i, addr in enumerate(NODOS_FILLS):
    inicio = i * tamano_particion
    fin = (i + 1) * tamano_particion if i < (len(NODOS_FILLS)-1) else len(imagenes_brutas)
    
    # Convertimos la sub-lista en un array de NumPy continuo y luego a bytes
    particion_np = np.array(imagenes_brutas[inicio:fin])
    payload_bytes = particion_np.tobytes()
    
    datos_preparados.append((addr, payload_bytes, i))

def enviar_tarea_grpc(config):
    addr, payload, batch_id = config
    MAX_MESSAGE_LENGTH = 200 * 1024 * 1024
    
    payload_size = len(payload)
    inicio_rtt = time.perf_counter() # Cronómetro RTT
    
    try:
        with grpc.insecure_channel(
            addr, 
            options=[
                ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
                ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH)
            ]
        ) as channel:
            stub = mnist_pb2_grpc.MnistServiceStub(channel)
            peticion = mnist_pb2.BatchRequest(batch_id=batch_id, image_data=payload)
            response = stub.ProcessBatch(peticion, timeout=300)
            
        fin_rtt = time.perf_counter()
        
        return {
            "ram_max_mb": response.ram_usage,
            "cpu_promedio": response.cpu_usage,
            "t_proc_ms": response.t_proc_ms,
            "rtt_ms": (fin_rtt - inicio_rtt) * 1000,
            "payload_bytes": payload_size,
            "imagenes_contadas": response.images_processed
        }
    except Exception as e:
        print(f"Error en {addr}: {e}")
        return {"error": str(e), "addr": addr}

# --- Ejecución ---
print(f"Lanzando proceso gRPC en {len(NODOS_FILLS)} nodos...")
inicio_t = time.perf_counter() # Uso correcto del perf_counter global

with ThreadPoolExecutor(max_workers=len(NODOS_FILLS)) as executor:
    resultados = list(executor.map(enviar_tarea_grpc, datos_preparados))

fin_t = time.perf_counter()

# --- Consolidación ---
tiempo_total = fin_t - inicio_t
exitos = [r for r in resultados if "error" not in r]

tasa_exito = (len(exitos) / len(NODOS_FILLS)) * 100
throughput = len(imagenes_brutas) / tiempo_total

if exitos:
    ram_pico_max = max(r["ram_max_mb"] for r in exitos)
    cpu_media = sum(r["cpu_promedio"] for r in exitos) / len(exitos)
    rtt_medio = sum(r["rtt_ms"] for r in exitos) / len(exitos)
    t_proc_medio = sum(r["t_proc_ms"] for r in exitos) / len(exitos)
    payload_total_mb = sum(r["payload_bytes"] for r in exitos) / (1024 * 1024)
else:
    ram_pico_max = cpu_media = rtt_medio = t_proc_medio = payload_total_mb = 0

payload_promedio_nodo = payload_total_mb / len(exitos) if exitos else 0

# --- Tabla Final ---
print("\n" + "="*50)
print(" RESULTADOS DE LA COMPARATIVA TÉCNICA ")
print("="*50)
print(f"{'Protocolo de Comunicación:':<30} gRPC (Protobuf/Binary)")
print(f"{'Tiempo Total (s):':<30} {tiempo_total:.2f} s")
print(f"{'Throughput (img/s):':<30} {throughput:.2f} img/s")
print(f"{'Latencia RTT Promedio (ms):':<30} {rtt_medio:.2f} ms")
print(f"{'Tiempo T_proc Promedio (ms):':<30} {t_proc_medio:.2f} ms")
print(f"{'Pico Máx. RAM Worker (MB):':<30} {ram_pico_max:.2f} MB")
print(f"{'CPU Promedio (%):':<30} {cpu_media:.2f} %")
print(f"{'Payload Promedio por Nodo (MB):':<30} {payload_promedio_nodo:.2f} MB")
print(f"{'Datos Totales Red (MB):':<30} {payload_total_mb:.2f} MB")
print(f"{'Tasa Éxito (%):':<30} {tasa_exito:.2f} %")
print("="*50)