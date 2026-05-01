# Arquitectura de Orquestación Edge: Implementación HTTP/REST

Este repositorio documenta la primera versión de la comparativa de protocolos de red para arquitecturas distribuidas en entornos Edge Computing. Esta implementación establece el *baseline* o línea de referencia utilizando el estándar de la industria web: el protocolo HTTP/1.1 con serialización JSON bajo un patrón arquitectónico Master-Worker.

## Diseño de la Arquitectura (Master-Worker)

El sistema se estructura en dos capas principales, diseñadas para la distribución de cargas de trabajo de visión artificial (dataset MNIST).

### 1. El Nodo Orquestador (Master)
El nodo central (`master.py`) actúa como el coordinador y distribuidor de la carga. Sus responsabilidades técnicas incluyen:
*   **Ingesta y Preprocesamiento:** Carga el dataset de entrenamiento MNIST utilizando `tensorflow-datasets`. A continuación, convierte los arrays brutos de NumPy en listas nativas de Python (`.tolist()`) para permitir su posterior serialización en JSON.
*   **Partición de Datos:** Divide el volumen total de imágenes en fragmentos (chunks) equitativos en función del número de nodos Worker disponibles en el clúster.
*   **Concurrencia de Red:** Implementa un `ThreadPoolExecutor` para lanzar peticiones POST HTTP en paralelo (multihilo) hacia las IPs de los nodos Workers, evitando el bloqueo síncrono y midiendo el tiempo global de procesamiento (Throughput).

### 2. Los Nodos Perimetrales (Workers)
Los dispositivos del clúster (ej: `192.168.98.143` y `144`) ejecutan contenedores *rootless* gestionados por Quadlets, que actúan como sumideros de datos pasivos.
*   **Framework API:** Cada contenedor expone un servidor ASGI (`Uvicorn`) en el puerto 8000, orquestado por el microframework `FastAPI`.
*   **Procesamiento y Telemetría:** El endpoint `/procesar` recibe la partición de datos, ejecuta la tarea simulada (conteo de imágenes) y utiliza la librería `psutil` para inspeccionar el uso de memoria RAM (RSS) y CPU del propio proceso antes de devolver el *payload* de respuesta.

## Protocolo y Formato de Serialización

Esta iteración fuerza el uso de tecnologías web tradicionales en un entorno distribuido perimetral:

*   **Capa de Transporte (HTTP/1.1):** La comunicación se realiza mediante peticiones HTTP estándar gestionadas por la librería `requests` en el Master. Esto introduce latencia inherente debido a la negociación de cabeceras y la apertura de conexiones individuales por cada transacción.
*   **Capa de Serialización (JSON):** El formato de intercambio de datos es texto plano estructurado (JSON). El Master serializa el array multidimensional de píxeles (`{"imagenes": particion}`), y FastAPI en los Workers se encarga del *parsing* asíncrono para reconstruir los datos en memoria antes del cómputo.

## Despliegue con Ansible

La infraestructura se aprovisiona mediante Ansible, inyectando el código de los Workers en contenedores basados en `python:3.11-slim`. Para desplegar este protocolo específico, la variable de entorno en el inventario debe apuntar al directorio correcto:

```yaml
# En el archivo de variables o inventario de Ansible
experimento_path: "../results/http"
```

## Análisis de Rendimiento (resultados en `experiments.md`)

Las pruebas de estrés sobre la implementación HTTP/REST arrojan métricas que evidencian los cuellos de botella de la serialización en texto plano para grandes volúmenes de datos binarios.

Basado en las ejecuciones de prueba (Test 1-5):
*   **Tiempo Promedio de Ejecución:** ~13.33 segundos.
*   **Saturación de Memoria (RAM):** El proceso de *parsing* del inmenso objeto JSON obliga a Python a consumir un promedio superior a los **2.6 GB de RAM** por cada Worker.
*   **Eficiencia de Red:** La transmisión en texto plano requiere mover un *payload* de aproximadamente **242.29 MB** por el enlace de red, limitando el Throughput general del clúster a unas 4.600 imágenes/segundo de media.

### RESULTADOS: HTTP/REST (JSON)

| Prueba | Tiempo Total (s) | Throughput (img/s) | RAM Máx, Worker (MB) | CPU Promedio (%) | Datos Totales Red (MB) | Tasa Éxito (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Test 1** | 17,87 | 3357,91 | 2621,75 MB | 8,40% | 242,29 MB | 100,00% |
| **Test 2** | 13,39 | 4482,42 | 2631,48 MB | 1,05% | 242,29 MB | 100,00% |
| **Test 3** | 11,6 | 5170,64 | 2631,48 MB | 1,50% | 242,29 MB | 100,00% |
| **Test 4** | 12,41 | 4833,97 | 2631,48 MB | 0,40% | 242,29 MB | 100,00% |
| **Test 5** | 11,38 | 5274,69 | 2631,48 MB | 4,65% | 242,29 MB | 100,00% |
| **Total** | **13,33** | **4623,926** | **2631,48 MB** | **3,20%** | **242,29 MB** | **100,00%** |


## Guía de Ejecución: Clúster Edge MNIST (HTTP/REST)

### 1. Preparación del Entorno (Master)
Preparar el entorno virtual del nodo orquestador con las dependencias para ingestar el dataset y hacer peticiones web.
```bash
# Instalar dependencias necesarias en el Master
pip install tensorflow-datasets numpy requests
```

### 2. Despliegue de Infraestructura (Ansible)
Asegúrate de que la variable `experimento_path` de tu inventario apunta a la carpeta de HTTP (`"../results/http"`). Luego, usa Ansible para configurar Podman, la red interna y los Quadlets de Systemd en los nodos.
```bash
# 1. Limpiar cualquier rastro previo de otros protocolos (Recomendado)
ansible-playbook -i inventory.ini clean.yml -K

# 2. Desplegar y arrancar el clúster con la API de FastAPI
ansible-playbook -i inventory.ini playbook.yml -K
```

### 3. Verificación en los Nodos (Workers)
Si quieres comprobar que los contenedores están corriendo bajo Systemd (modo *rootless*) y que Uvicorn está escuchando correctamente en el puerto 8000:
```bash
# Conectarse a uno de los nodos (ej. node-a)
ssh littledragon@192.168.98.143

# Ver el estado del servicio gestionado por Systemd
systemctl --user status worker.service

# Ver logs en tiempo real del servidor FastAPI/Uvicorn
journalctl --user -u worker.service -f
```

### 4. Ejecución del Experimento (Master)
Una vez que los Workers muestren el estado `running` y Uvicorn esté listo, lanza el script principal desde tu máquina orquestadora para enviar las imágenes vía POST y obtener la tabla de resultados.
```bash
python master.py
```