import tensorflow_datasets as tfds
import numpy as np
import requests

# 1. Definimos nuestros N nodos (Parametrizable)
NODOS_FILLS = ["192.168.1.101", "192.168.1.102"] 
N_NODOS = len(NODOS_FILLS)

print("1. Conectando con TensorFlow Datasets para descargar MNIST...")
dataset = tfds.load('mnist', split='train', as_supervised=True)

print("2. Preparando datos (Solucionando el problema de JSON)...")
 
# Cuando veas que funciona, quita el .take(1000) para enviar las 60.000
imagenes_brutas = list(tfds.as_numpy(dataset.take(1000)))

lista_imagenes = [img.tolist() for img, label in imagenes_brutas]

total_imagenes = len(lista_imagenes)
print(f"¡Descarga completada! Total de imágenes a procesar: {total_imagenes}\n") 

tamano_particion = total_imagenes // N_NODOS
print(f"3. Dividiendo el dataset en {N_NODOS} partes de {tamano_particion} imágenes...\n")

# 4. Bucle mágico para enviar a N nodos
for i, ip_worker in enumerate(NODOS_FILLS):
    # Calculamos dónde empieza y dónde acaba el trozo para este worker
    inicio = i * tamano_particion
    # Si es el último nodo, le damos todo lo que sobre hasta el final
    fin = (i + 1) * tamano_particion if i < (N_NODOS - 1) else total_imagenes
    
    particion = lista_imagenes[inicio:fin]
    
    print(f"-> Enviando partición {i+1} ({len(particion)} imgs) al worker en {ip_worker}...")
    try:
        # Apuntamos directamente al puerto 8000 del worker (Saltándonos el balanceador)
        respuesta = requests.post(f"http://{ip_worker}:8000/procesar", json={"imagenes": particion})
        print(f"   [OK] Respuesta del {ip_worker}:", respuesta.json())
    except Exception as e:
        print(f"   [ERROR] Falló la conexión con {ip_worker}: {e}")