# Arquitectura de Orquestación Edge: Implementación HTTP/REST

Esta sección del proyecto alberga la primera versión de la comparativa de protocolos de red para arquitecturas distribuidas en entornos Edge Computing. Esta implementación establece el *baseline* o línea de referencia utilizando el estándar de la industria web: el protocolo HTTP/1.1 con serialización JSON (texto plano) bajo un patrón arquitectónico Master-Worker.

## Diseño de la Arquitectura (Master-Worker)

El sistema se estructura en dos capas principales, diseñadas para la distribución de cargas de trabajo de visión artificial (dataset MNIST).

### 1. El Nodo Orquestador (Master)

El nodo central (`master.py`) actúa como el coordinador y distribuidor de la carga. Sus responsabilidades técnicas incluyen:

* **Ingesta y Preprocesamiento:** Carga el dataset de entrenamiento MNIST utilizando `tensorflow-datasets`. A continuación, convierte los tensores brutos de NumPy en listas nativas de Python (`.tolist()`) para permitir su posterior serialización.
* **Partición de Datos:** Divide el volumen total de imágenes en fragmentos (*chunks*) equitativos en función del número de nodos Worker disponibles en el clúster.
* **Aislamiento de Métricas y Serialización:** Antes de iniciar la transmisión, el Master transforma la partición a texto estructurado (`json.dumps()`). Esta operación de serialización se ejecuta **fuera del cronómetro de latencia**, garantizando que el cálculo del RTT mida de forma estricta el tiempo de tránsito en red y el procesamiento en el Edge, sin interferencias del propio orquestador.
* **Concurrencia de Red:** Implementa un `ThreadPoolExecutor` para lanzar peticiones POST HTTP en paralelo (multihilo) hacia las IPs de los nodos Workers. El código utiliza relojes de alta resolución (`time.perf_counter()`) para medir con precisión nanométrica el tiempo global de procesamiento (Throughput) y la latencia individual de cada conexión.

### 2. Los Nodos Perimetrales (Workers)

Los dispositivos del clúster (ej: `192.168.98.143` y `144`) ejecutan contenedores *rootless* gestionados por Quadlets de Systemd, que actúan como sumideros de datos.

* **Framework API Asíncrono:** Cada contenedor expone un servidor ASGI (`Uvicorn`) en el puerto 8000, orquestado por el microframework `FastAPI`. La ruta `/procesar` está definida como una corrutina (`async def`), permitiendo la gestión eficiente del I/O de red antes de bloquear el hilo con el cómputo.
* **Deserialización (El Cuello de Botella):** El endpoint asume la tarea intensiva de reconstruir el objeto en memoria mediante `await request.json()`. Es precisamente en esta instrucción de *parsing* de texto plano a diccionarios nativos donde recae la saturación de los núcleos del procesador documentada en los resultados empíricos.
* **Telemetría de Alta Precisión In-situ:** El Worker no solo procesa los datos, sino que se auto-monitoriza aislando su propio identificador de proceso (`os.getpid()`). Se utiliza la librería `psutil` aplicando una técnica de "limpieza de buffer" (`cpu_percent(interval=None)`) justo antes de iniciar la medición. Esto garantiza que la métrica de CPU devuelta corresponda exclusivamente al esfuerzo de procesar la petición actual, eliminando el ruido de fondo del sistema operativo subyacente.
* **Aislamiento del Tiempo de Procesamiento ($T_{proc}$):** Utilizando relojes de alta resolución (`time.perf_counter()`), el Worker cronometra los milisegundos exactos que invierte en la deserialización y lectura de memoria (RAM RSS real), empaquetando estas métricas de rendimiento en la respuesta JSON para que el Master pueda consolidar la telemetría global.

## Protocolo y Formato de Serialización

Esta iteración fuerza el uso de tecnologías web tradicionales en un entorno distribuido perimetral:

* **Capa de Transporte (HTTP/1.1):** La comunicación se realiza mediante peticiones HTTP estándar gestionadas por la librería `requests` en el Master. Esto introduce latencia inherente debido a la negociación de cabeceras y la apertura de conexiones individuales por cada transacción.
* **Capa de Serialización (JSON):** El formato de intercambio de datos es texto plano estructurado (JSON). El Master serializa el array multidimensional de píxeles (`{"imagenes": particion}`), y FastAPI en los Workers se encarga del *parsing* asíncrono para reconstruir los datos en memoria antes del cómputo. Al no soportar transmisión binaria nativa, el envío de matrices de píxeles exige convertirlas a enormes listas de texto (o alternativamente codificarlas en Base64). Esta limitación del estándar web infla el tamaño del payload original en más de un 33% (penalización de red) y obliga a los Workers a realizar un parsing asíncrono extremadamente ineficiente, saturando la CPU solo para reconstruir los datos en memoria.

## Despliegue con Ansible

La infraestructura se aprovisiona mediante Ansible, inyectando el código de los Workers en contenedores basados en `python:3.11-slim`. Para desplegar este protocolo específico, puedes configurar el inventario por defecto o inyectar la variable de ruta en tiempo de ejecución:

```bash
# Por defecto configurado en inventario de Ansible
ansible-playbook -i inventory.ini playbook.yml

# O inyectando la variable dinámicamente
ansible-playbook -i inventory.ini playbook.yml -e "experimento_path=../2-src-protocols/01-http-json"
```

---

## Guía de Ejecución: Clúster Edge MNIST (HTTP/REST)

```bash
# Instalar dependencias necesarias en el Master
pip install tensorflow-datasets numpy requests

# Ejecutar nodo Master
python3 master.py
```