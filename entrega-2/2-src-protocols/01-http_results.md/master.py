import tensorflow_datasets as tfds
import requests
import time
import json
from concurrent.futures import ThreadPoolExecutor

# Configuración del entorno
NODOS_FILLS = ["192.168.98.143", "192.168.98.144"] 

print("Cargando MNIST...")
dataset = tfds.load('mnist', split='train', as_supervised=True)
imagenes_brutas = list(tfds.as_numpy(dataset))
lista_imagenes = [img.tolist() for img, label in imagenes_brutas]

# Preparación de particiones
tamano_particion = len(lista_imagenes) // len(NODOS_FILLS)
datos_preparados = []

for i, ip in enumerate(NODOS_FILLS):
    inicio = i * tamano_particion
    fin = (i + 1) * tamano_particion if i < (len(NODOS_FILLS)-1) else len(lista_imagenes)
    particion = lista_imagenes[inicio:fin]
    datos_preparados.append((ip, {"imagenes": particion}))

def enviar_tarea(config):
    ip, payload_dict = config
    
    # Serializamos ANTES del RTT para medir el payload real que sale al cable
    payload_str = json.dumps(payload_dict)
    payload_bytes = len(payload_str.encode('utf-8'))
    
    inicio_rtt = time.perf_counter() # perf_counter es más preciso para RTT
    try:
        res = requests.post(f"http://{ip}:8000/procesar", data=payload_str, 
                            headers={'Content-Type': 'application/json'}, timeout=300)
        fin_rtt = time.perf_counter()
        
        datos_worker = res.json()
        datos_worker["rtt_ms"] = (fin_rtt - inicio_rtt) * 1000
        datos_worker["payload_bytes"] = payload_bytes
        return datos_worker
    except Exception as e:
        return {"error": str(e), "ip": ip}

# --- Ejecución y Cronometraje Global ---
print(f"Lanzando proceso distribuido en {len(NODOS_FILLS)} nodos...")
inicio_t = time.perf_counter()

with ThreadPoolExecutor(max_workers=len(NODOS_FILLS)) as executor:
    resultados = list(executor.map(enviar_tarea, datos_preparados))

fin_t = time.perf_counter()

# --- Consolidación de Resultados ---
tiempo_total = fin_t - inicio_t
exitos = [r for r in resultados if "error" not in r]

tasa_exito = (len(exitos) / len(NODOS_FILLS)) * 100
throughput = len(lista_imagenes) / tiempo_total

# Cálculos de promedios y sumatorios extraídos de los workers
if exitos:
    ram_pico_max = max(r["ram_max_mb"] for r in exitos) # El peor caso de RAM
    cpu_media = sum(r["cpu_promedio"] for r in exitos) / len(exitos)
    rtt_medio = sum(r["rtt_ms"] for r in exitos) / len(exitos)
    t_proc_medio = sum(r["t_proc_ms"] for r in exitos) / len(exitos)
    payload_total_mb = sum(r["payload_bytes"] for r in exitos) / (1024 * 1024)
    payload_promedio_nodo = payload_total_mb / len(exitos)
else:
    ram_pico_max = cpu_media = rtt_medio = t_proc_medio = payload_total_mb = 0

# --- Impresión de la Tabla Final ---
print("\n" + "="*50)
print(" RESULTADOS DE LA COMPARATIVA TÉCNICA ")
print("="*50)
print(f"{'Protocolo de Comunicación:':<30} HTTP/REST (JSON)")
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