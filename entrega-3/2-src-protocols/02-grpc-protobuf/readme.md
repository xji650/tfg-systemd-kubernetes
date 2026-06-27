# Arquitectura de Orquestación Edge: Implementación gRPC

Este directorio documenta la segunda versión de la comparativa de protocolos de red para arquitecturas distribuidas en entornos Edge Computing. En esta fase, se abandona el estándar web tradicional en favor de **gRPC y Protocol Buffers (Protobuf)**, un framework de Llamada a Procedimiento Remoto (RPC) de alto rendimiento, ideal para la transmisión eficiente de datos binarios masivos.

## Diseño de la Arquitectura (Master-Worker)

El sistema evoluciona hacia un modelo de comunicación basado en contratos estrictos, optimizando tanto el empaquetado de datos como la huella de memoria (RAM) al eliminar la serialización en texto plano.

### 1. El Nodo Orquestador (Master)
El script `master.py` actúa como cliente gRPC y distribuidor de la carga de visión artificial. Sus mejoras técnicas incluyen:

* **Conversión Binaria Nativa (Zero-Copy):** Carga el dataset MNIST como matrices `float32` de NumPy. En lugar de iterar y parsear a listas JSON, inyecta los datos directamente en crudo mediante `particion_np.tobytes()`, eliminando el *overhead* de transformación.
* **Ajuste de Ventanas TCP/gRPC:** Por diseño, gRPC impone un límite estricto de 4 MB por mensaje por motivos de seguridad. Dado el volumen de las particiones, el Master reconfigura los canales asíncronos sobrescribiendo `grpc.max_send_message_length` y `max_receive_message_length` a **200 MB**, permitiendo la transmisión ininterrumpida de grandes tensores.
* **Aislamiento de Métricas:** Se utilizan relojes de alta resolución (`time.perf_counter()`) para medir el RTT exacto de la llamada a procedimiento remoto de forma aislada.

### 2. Contrato de Datos (Protobuf)
El intercambio se rige por un Interface Definition Language (IDL) definido en `mnist.proto`. Esto garantiza un tipado fuerte de las variables (`int32`, `bytes`, `float`) y comprime la transmisión al eliminar la basura sintáctica (llaves, comas, comillas) inherente a JSON.

* **Justificación del Payload:** Se procesan 30.000 imágenes por nodo. Cada imagen (28x28) consta de 784 píxeles `float32` (4 bytes/píxel). La huella binaria matemática en la red es de exactamente 94.080.000 bytes ($\approx 89.72$ MB estandarizados).

### 3. Los Nodos Perimetrales (Workers)
Los contenedores *rootless* (Quadlets) ejecutan un servidor gRPC instanciado en el puerto 8000.

* **Servidor RPC:** La clase `MnistServicer` implementa el método `ProcessBatch` derivado de los *stubs* generados por el compilador Protobuf.
* **Zero-Parsing en Memoria:** Al recibir el payload binario (`request.image_data`), el Worker lo asigna directamente a la memoria de la CPU utilizando `np.frombuffer(..., dtype=np.float32)`. Esta instrucción actúa como un puntero de memoria, erradicando por completo el tiempo intensivo de deserialización iterativa.
* **Telemetría Integrada:** Se ejecuta una limpieza de buffers (`cpu_percent(interval=None)`) antes de procesar el tensor binario, devolviendo al Master un objeto `BatchResponse` fuertemente tipado con los consumos exactos de hardware ($T_{proc}$, RAM y CPU).

## Protocolo y Formato de Serialización

* **Capa de Transporte (HTTP/2):** gRPC opera nativamente sobre HTTP/2, permitiendo multiplexación real sobre una única conexión TCP.
* **Capa de Serialización (Protobuf):** El intercambio de datos se realiza de forma binaria, reduciendo significativamente el ancho de banda necesario respecto a la versión HTTP/REST.

## Despliegue con Ansible

La infraestructura se aprovisiona inyectando la ruta del directorio gRPC. Dado que el archivo de variables del repositorio apunta por defecto a HTTP, para este protocolo **es obligatorio** inyectar la variable dinámicamente por terminal. Los contenedores instalarán las herramientas base y compilarán automáticamente el `.proto` en su interior durante la fase de *build* orquestada por Systemd.

```bash
# Desplegar inyectando la ruta de gRPC para sobrescribir el valor por defecto
ansible-playbook -i inventory.ini playbook.yml -e "experimento_path=../2-src-protocols/02-grpc-proto"
```

---

## Guía de Ejecución: Clúster Edge MNIST (gRPC)

### 1. Preparación del Entorno (Master)

Antes de ejecutar el orquestador, se deben instalar las librerías base y compilar el contrato `.proto` para generar los *stubs* de red (`_pb2.py` y `_pb2_grpc.py`).

```bash
# Instalar dependencias necesarias
pip install grpcio grpcio-tools psutil numpy tensorflow-datasets

# Compilar el contrato Protobuf
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. edge.proto
```

### 2. Despliegue de Infraestructura (Ansible)

Asegúrate de que la variable `experimento_path` apunta a la carpeta de gRPC (`../2-src-protocols/02-grpc-proto`).

```bash
# 1. Limpiar cualquier rastro previo del protocolo HTTP
ansible-playbook -i inventory.ini clean.yml

# 2. Desplegar y arrancar el clúster inyectando el código gRPC
ansible-playbook -i inventory.ini playbook.yml -e "experimento_path=../2-src-protocols/02-grpc-proto"
```

### 3. Verificación en los Nodos (Workers)

Si quieres comprobar que los contenedores están corriendo y que el servidor de RPC está listo en el puerto 8000:

```bash
# Conectarse al nodo
ssh littledragon@192.168.98.143

# Ver el estado del servicio
systemctl --user status worker.service

# Ver logs (debe indicar "Servidor gRPC iniciado (Límite 200MB)")
journalctl --user -u worker.service -f
```

### 4. Ejecución del Experimento (Master)

Una vez validado el clúster, lanza el script principal para inyectar la carga. Los resultados crudos se imprimirán en consola para su posterior consolidación en la matriz de métricas de la Parte 03.

```bash
python master.py
```
