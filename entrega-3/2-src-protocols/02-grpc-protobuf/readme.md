# Arquitectura de Orquestación Edge: Implementación gRPC con Inteligencia Artificial

Este directorio documenta la segunda versión de la comparativa de protocolos de red para arquitecturas distribuidas en entornos Edge Computing. En esta fase, se abandona el estándar web tradicional en favor de **gRPC y Protocol Buffers (Protobuf)**, un framework de Llamada a Procedimiento Remoto (RPC) de alto rendimiento.

Al igual que la fase base, esta iteración ejecuta el ciclo de vida completo de un modelo de **Machine Learning (PyTorch)**. Sin embargo, demuestra cómo un protocolo estrictamente tipado y de transmisión binaria elimina los cuellos de botella de red (*I/O Bound*), exponiendo el verdadero límite de hardware de los dispositivos Edge en inferencia de Redes Neuronales Convolucionales (*Compute Bound*).

## Diseño de la Arquitectura (Master-Worker)

El sistema evoluciona hacia un modelo de comunicación basado en contratos estrictos, optimizando el empaquetado de datos y reduciendo drásticamente la huella de memoria (RAM) al erradicar la deserialización de texto plano.

### 1. El Nodo Orquestador (Master)

El script `master.py` actúa como cliente gRPC y distribuidor de la carga de visión artificial, ejecutando cuatro fases secuenciales:

* **Fase 1: Entrenamiento y Artefactos (Offline):** El Master entrena una red neuronal CNN durante 1 época (o la recupera de la caché local). Exporta métricas visuales a la carpeta `assets/` y genera el binario de pesos neuronales `best_model.pth`.
* **Fase 2: Distribución del Modelo (Upload gRPC):** A diferencia de HTTP, utiliza un canal asíncrono RPC (`UploadModel`) para inyectar el archivo binario del modelo directamente en los nodos remotos superando las limitaciones estándar de tamaño de mensaje.
* **Fase 3: Conversión Binaria Nativa (Zero-Copy):** En lugar de iterar iterativamente para generar largas cadenas JSON, el Master convierte el dataset completo a matrices `float32` de NumPy e inyecta los datos en crudo directamente a nivel de C mediante `particion_np.tobytes()`. Esto elimina el 100% del *overhead* de transformación de datos.
* **Fase 4: Inferencia y Ajuste de Ventanas TCP:** gRPC impone un límite de seguridad estricto de 4 MB por mensaje. El Master reconfigura los canales sobrescribiendo `grpc.max_send_message_length` a **200 MB**. Se lanzan los hilos paralelos y se aíslan los tiempos de RTT, generando finalmente el mosaico visual de validación (`ejemplos-predicciones-grpc.png`).

### 2. Contrato de Datos (Protobuf)

El intercambio se rige por un Interface Definition Language (IDL) definido en `mnist.proto`. Esto garantiza un tipado fuerte de las variables y comprime la transmisión al eliminar la basura sintáctica (llaves, comas, comillas).

* **Servicio Dual:** El `.proto` define dos endpoints RPC diferenciados: uno para inicializar la infraestructura (`ModelRequest`) y otro para la inferencia pura (`BatchRequest`).
* **Optimización Extrema del Payload:** Al usar `bytes` puros, enviar particiones de 1000 imágenes (28x28 píxeles en formato `float32` de 4 bytes) resulta en un peso de red exacto de **2.99 MB**, comparado con los >15 MB que requiere la misma matriz serializada en texto JSON.

### 3. Los Nodos Perimetrales (Workers)

Los contenedores *rootless* (Quadlets) ejecutan un servidor gRPC instanciado en el puerto 8000 mediante la clase `MnistServicer`.

* **Carga Dinámica RPC:** El método `UploadModel` recibe los bytes del modelo `.pth`, los vuelca a disco localmente y los transfiere a la VRAM/RAM de PyTorch poniéndolo en estado `model.eval()`.
* **Zero-Parsing en Memoria:** Al recibir la carga de imágenes, el método `Procesar` aplica el concepto de *Zero-Parsing*. Mediante la instrucción `np.frombuffer(..., dtype=np.float32)`, el sistema operativo asigna un puntero directo a la memoria, erradicando por completo el tiempo de CPU desperdiciado en interpretar datos.
* **El Cuello de Botella Híbrido:** Como la red y el *parsing* operan en milisegundos, toda la carga recae exclusivamente en los núcleos matemáticos procesando las capas ocultas de PyTorch (`torch.no_grad()`).
* **Telemetría Integrada:** Se ejecuta una limpieza de buffers de sistema (`cpu_percent(interval=None)`) antes y después del procesamiento matemático, devolviendo al Master un objeto tipado `BatchResponse` con el impacto real en el hardware ($T_{proc}$, RAM y CPU).

## Protocolo y Formato de Serialización

* **Capa de Transporte (HTTP/2):** gRPC opera nativamente sobre HTTP/2, permitiendo multiplexación bidireccional sobre una única conexión TCP de larga duración.
* **Capa de Serialización (Protobuf):** Binaria, estructurada y precompilada. Permite la ejecución de código C++ / Cython optimizado por debajo del motor de Python.

## Despliegue con Ansible

La infraestructura se aprovisiona mediante Ansible. Los contenedores instalarán las librerías matemáticas pesadas y compilarán automáticamente el contrato `.proto` durante la fase de *build* orquestada por Systemd.

```bash
# Inyectando la variable de ruta al directorio correspondiente
ansible-playbook -i inventory.ini playbook.yml -e "experimento_path=../2-src-protocols/02-grpc-protobuf"
```

---

## Guía de Ejecución: Clúster Edge MNIST (gRPC)

### 1. Preparación del Entorno (Master)

Antes de ejecutar el orquestador, debes instalar las dependencias científicas, las de red, y compilar el contrato `.proto` para generar los *stubs* de Python (`_pb2.py` y `_pb2_grpc.py`).

```bash
# 1. Instalar dependencias necesarias
pip install grpcio grpcio-tools psutil numpy torch torchvision matplotlib seaborn scikit-learn

# 2. Compilar el contrato Protobuf
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. mnist.proto
```

### 2. Despliegue de Infraestructura (Ansible)

Asegúrate de que la variable `experimento_path` apunta a la carpeta de gRPC (ej: `../2-src-protocols/02-grpc-protobuf`).

```bash
# 1. Limpiar cualquier rastro previo del protocolo HTTP
ansible-playbook -i inventory.ini clean.yml

# 2. Desplegar y arrancar el clúster inyectando el código gRPC
ansible-playbook -i inventory.ini playbook.yml -e "experimento_path=../2-src-protocols/02-grpc-protobuf"
```

### 3. Verificación en los Nodos (Workers)

Comprueba que el Quadlet de Systemd ha levantado el contenedor correctamente y que gRPC está a la escucha (este proceso puede tardar unos minutos en el primer despliegue debido a la descarga de PyTorch en los nodos):

```bash
# Conectarse al nodo perimetral
ssh littledragon@192.168.98.143

# Ver el estado del servicio
systemctl --user status worker.service

# Ver logs (debe indicar "Iniciando Worker Edge IA (gRPC/Protobuf) en puerto 8000...")
journalctl --user -u worker.service -f
```

### 4. Ejecución del Experimento (Master)

Una vez validado el clúster, lanza el script principal. Verás en tu consola cómo el Master entrena el modelo (si no está en caché), transfiere el `.pth` vía gRPC, y lanza la batería de pruebas masivas, mostrando la telemetría en tiempo real:

```bash
python master.py
```
