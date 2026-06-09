# Arquitectura de Orquestación Edge: Implementación HTTP/REST

Este repositorio documenta la primera versión de la comparativa de protocolos de red para arquitecturas distribuidas en entornos Edge Computing. Esta implementación establece el *baseline* o línea de referencia utilizando el estándar de la industria web: el protocolo HTTP/1.1 con serialización JSON bajo un patrón arquitectónico Master-Worker.

## Diseño de la Arquitectura (Master-Worker)

El sistema se estructura en dos capas principales, diseñadas para la distribución de cargas de trabajo de visión artificial (dataset MNIST).

### 1. El Nodo Orquestador (Master)
El nodo central (`master.py`) actúa como el coordinador y distribuidor de la carga. Sus responsabilidades técnicas incluyen:

* **Ingesta y Preprocesamiento:** Carga el dataset de entrenamiento MNIST utilizando `tensorflow-datasets`. A continuación, convierte los arrays brutos de NumPy en listas nativas de Python (`.tolist()`) para permitir su posterior serialización en JSON.
* **Partición de Datos:** Divide el volumen total de imágenes en fragmentos (chunks) equitativos en función del número de nodos Worker disponibles en el clúster.
* **Concurrencia de Red:** Implementa un `ThreadPoolExecutor` para lanzar peticiones POST HTTP en paralelo (multihilo) hacia las IPs de los nodos Workers, evitando el bloqueo síncrono y midiendo el tiempo global de procesamiento (Throughput).

### 2. Los Nodos Perimetrales (Workers)
Los dispositivos del clúster (ej: `192.168.98.143` y `144`) ejecutan contenedores *rootless* gestionados por Quadlets, que actúan como sumideros de datos pasivos.

* **Framework API:** Cada contenedor expone un servidor ASGI (`Uvicorn`) en el puerto 8000, orquestado por el microframework `FastAPI`.
* **Procesamiento y Telemetría:** El endpoint `/procesar` recibe la partición de datos, ejecuta la tarea simulada (conteo de imágenes) y utiliza la librería `psutil` para inspeccionar el uso de memoria RAM (RSS) y la carga de CPU del propio proceso de forma aislada, devolviendo estas métricas junto al *payload* de respuesta.

## Protocolo y Formato de Serialización

Esta iteración fuerza el uso de tecnologías web tradicionales en un entorno distribuido perimetral:

* **Capa de Transporte (HTTP/1.1):** La comunicación se realiza mediante peticiones HTTP estándar gestionadas por la librería `requests` en el Master. Esto introduce latencia inherente debido a la negociación de cabeceras y la apertura de conexiones individuales por cada transacción.
* **Capa de Serialización (JSON):** El formato de intercambio de datos es texto plano estructurado (JSON). El Master serializa el array multidimensional de píxeles (`{"imagenes": particion}`), y FastAPI en los Workers se encarga del *parsing* asíncrono para reconstruir los datos en memoria antes del cómputo.

## Despliegue con Ansible

La infraestructura se aprovisiona mediante Ansible, inyectando el código de los Workers en contenedores basados en `python:3.11-slim`. Para desplegar este protocolo específico, la variable de entorno en el inventario debe apuntar al directorio correcto:

```yaml
# En el archivo de variables o inventario de Ansible
experimento_path: "../results/http"
```

## Análisis de Rendimiento (resultados en `experiments.md`)

Las pruebas de rendimiento sobre la implementación HTTP/REST arrojan métricas concluyentes que evidencian el coste computacional de utilizar texto plano para grandes volúmenes de datos binarios en arquitecturas perimetrales.

Basado en las 5 ejecuciones de prueba realizadas, se extraen las siguientes conclusiones técnicas:

* **Cuello de Botella Computacional (CPU-Bound):** El consumo promedio de CPU en los Workers supera el **99.2%**. Esto demuestra que la deserialización del inmenso objeto JSON satura los núcleos del procesador.
* **Latencia de Red vs. Procesamiento:** Al comparar el RTT Promedio (~6710 ms) con el Tiempo de Procesamiento $T_{proc}$ (~6616 ms), se observa que el tiempo de tránsito en la red es marginal (apenas ~90 ms de *overhead*). El 98% del tiempo invertido corresponde a la CPU intentando parsear el texto.
* **Saturación de Memoria (RAM):** El proceso de carga del JSON en la memoria del Worker eleva el uso de RAM a un promedio sostenido de **~2.6 GB** (2597.5 MB) por contenedor.
* **Eficiencia de Carga Útil:** La transmisión requiere un *payload* de **121.14 MB por nodo**, sumando un total de **242.29 MB** en la red por cada ejecución completa. Pese al sobrecoste, el clúster alcanza un Throughput nada desdeñable de **~4985 imágenes/segundo**.

### TABLA RESUMEN: HTTP/REST (JSON)

| Prueba | Tiempo Total (s) | Throughput (img/s) | RTT Promedio (ms) | T_proc Promedio (ms) | Pico RAM Worker (MB) | CPU Promedio (%) | Datos Totales Red (MB) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Test 1** | 11.62 | 5164.92 | 6319.31 | 6189.05 | 2597.26 | 99.40 | 242.29 |
| **Test 2** | 11.65 | 5149.98 | 6481.46 | 6426.50 | 2597.34 | 99.20 | 242.29 |
| **Test 3** | 11.98 | 5009.94 | 6802.93 | 6702.05 | 2597.63 | 98.90 | 242.29 |
| **Test 4** | 11.93 | 5030.74 | 6365.22 | 6282.54 | 2597.56 | 99.05 | 242.29 |
| **Test 5** | 13.13 | 4569.61 | 7585.59 | 7480.69 | 2597.79 | 99.60 | 242.29 |
| **PROMEDIO** | **12.06** | **4985.04** | **6710.90** | **6616.17** | **2597.52** | **99.23** | **242.29** |

*(Nota: El Payload promedio por nodo se ha mantenido constante en 121.14 MB en todas las pruebas. La tasa de éxito en peticiones HTTP es del 100%).*

---

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