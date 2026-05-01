import tensorflow_datasets as tfds
import requests
import time
import sys
from concurrent.futures import ThreadPoolExecutor

# Configuración del entorno
NODOS_FILLS = ["192.168.98.143", "192.168.98.144"] 

print("Cargando MNIST...")
dataset = tfds.load('mnist', split='train', as_supervised=True)
imagenes_brutas = list(tfds.as_numpy(dataset))
lista_imagenes = [img.tolist() for img, label in imagenes_brutas]

# Preparación de métricas y particiones
tamano_particion = len(lista_imagenes) // len(NODOS_FILLS)
datos_preparados = []
bytes_totales = 0

for i, ip in enumerate(NODOS_FILLS):
    inicio = i * tamano_particion
    fin = (i + 1) * tamano_particion if i < (len(NODOS_FILLS)-1) else len(lista_imagenes)
    particion = lista_imagenes[inicio:fin]
    payload = {"imagenes": particion}
    bytes_totales += sys.getsizeof(str(payload)) # Estimación de red
    datos_preparados.append((ip, payload))

def enviar_tarea(config):
    ip, payload = config
    try:
        res = requests.post(f"http://{ip}:8000/procesar", json=payload, timeout=300)
        return res.json()
    except Exception as e:
        return {"error": str(e), "ip": ip}

# --- Ejecución y Cronometraje ---
print(f"Lanzando proceso distribuido en {len(NODOS_FILLS)} nodos...")
inicio_t = time.time()

with ThreadPoolExecutor(max_workers=len(NODOS_FILLS)) as executor:
    resultados = list(executor.map(enviar_tarea, datos_preparados))

fin_t = time.time()

# --- Consolidación de Resultados ---
tiempo_total = fin_t - inicio_t
exitos = [r for r in resultados if "error" not in r]
tasa_exito = (len(exitos) / len(NODOS_FILLS)) * 100
throughput = len(lista_imagenes) / tiempo_total
ram_media = sum(r["ram_mb"] for r in exitos) / len(exitos) if exitos else 0
cpu_media = sum(r["cpu_percent"] for r in exitos) / len(exitos) if exitos else 0

# --- Impresión de la Tabla Final ---
print("\n" + "="*50)
print(" RESULTADOS DE LA COMPARATIVA TÉCNICA ")
print("="*50)
print(f"{'Protocolo de Comunicación:':<30} HTTP/REST (JSON)")
print(f"{'Tiempo Total (s):':<30} {tiempo_total:.2f} s")
print(f"{'Throughput (img/s):':<30} {throughput:.2f} img/s")
print(f"{'RAM Máx. Worker (MB):':<30} {ram_media:.2f} MB")
print(f"{'CPU Promedio (%):':<30} {cpu_media:.2f} %")
print(f"{'Datos Totales Red (MB):':<30} {bytes_totales / (1024*1024):.2f} MB")
print(f"{'Tasa Éxito (%):':<30} {tasa_exito:.2f} %")
print("="*50)