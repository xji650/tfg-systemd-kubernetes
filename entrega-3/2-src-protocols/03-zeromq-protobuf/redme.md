# Arquitectura de Orquestación Edge: Implementación ZeroMQ (Protobuf) con Inteligencia Artificial

Este directorio documenta la tercera versión de la comparativa de protocolos de red para arquitecturas distribuidas en entornos Edge Computing. Tras validar la eficiencia de la serialización binaria en la fase anterior, esta iteración abandona por completo el estándar HTTP (incluyendo HTTP/2 de gRPC) para operar directamente sobre la capa de transporte TCP mediante **ZeroMQ (ZMQ)**, logrando el máximo rendimiento y la menor latencia de red posible.

Esta arquitectura integra el ciclo de vida completo de un modelo de **Machine Learning (PyTorch)**, demostrando qué ocurre cuando se combinan protocolos de comunicación ultraligeros con cargas de trabajo de IA computacionalmente intensivas (*Compute Bound*).

## Diseño de la Arquitectura (Master-Worker)

El sistema implementa el patrón de mensajería síncrona Request-Reply (REQ-REP) de ZeroMQ, manteniendo el tipado estricto de los datos pero asumiendo el control total del enrutamiento a nivel de aplicación.

### 1. El Nodo Orquestador (Master)

El script central actúa como cliente de red puro, inyectando los datos directamente a través de sockets TCP mediante cuatro fases:

* **Fase 1: Entrenamiento y Artefactos (Offline):** El Master entrena la red neuronal CNN y exporta las métricas visuales (`loss-curve.png`, `matriz-confusion.png`) a la carpeta `assets/`, guardando los pesos en `best_model.pth`.
* **Fase 2: Distribución del Modelo (Upload ZMQ):** Instancia un `zmq.Context()` y utiliza sockets `zmq.REQ`. A diferencia de gRPC, aquí se utiliza un envío multiparte (`send_multipart`) empaquetando el identificador `b"UPLOAD"` junto con los bytes crudos del modelo para transferir el cerebro de la IA a los nodos.
* **Fase 3: Conversión Binaria Nativa (Zero-Copy):** Reutilizando el contrato Protobuf (`BatchRequest`), el Master transforma las matrices `float32` de NumPy en una cadena de bytes pura (`SerializeToString()`) antes de iniciar la transmisión.
* **Fase 4: Inferencia y Resiliencia TCP:** Se establecen túneles concurrentes con cada IP del clúster. Puesto que ZeroMQ no implementa *timeouts* por defecto, se inyecta la directiva `socket.setsockopt(zmq.RCVTIMEO, 300000)` para evitar cuelgues infinitos. Finalmente, se genera el mosaico visual cruzando las predicciones devueltas.

### 2. El Contrato de Datos (Protobuf)

El intercambio de datos sigue regido por `mnist.proto`. Sin embargo, dado que operamos en ZeroMQ, no se utilizan directivas `service`. Solo definimos las estructuras de datos (mensajes), aislando la estructura del transporte.

* **Payload de Petición:** Transmisión pura mediante `bytes image_data`.


* **Payload de Respuesta:** Incluye telemetría y el vector con las predicciones de la IA (`repeated int32 predictions`).



### 3. Los Nodos Perimetrales (Workers)

Los contenedores *rootless* ejecutan un bucle de escucha asíncrono gestionado nativamente por `pyzmq`.

* **Socket Bind (REP) y Enrutamiento:** El servidor mapea un socket `zmq.REP` al puerto 8000. Al recibir mensajes, lee el primer *frame* (`b"UPLOAD"` o `b"INFER"`) para enrutar la lógica internamente, eliminando el *overhead* de los servidores web tradicionales.
* **Carga Dinámica en RAM:** Si el comando es `UPLOAD`, el Worker reconstruye el objeto `ModelRequest`, guarda el binario `.pth` y lo inyecta en la estructura neuronal de PyTorch (`model.eval()`).
* **Zero-Parsing y Cálculo Matemático:** Al recibir el comando `INFER`, el tensor se mapea instantáneamente en memoria utilizando `np.frombuffer(..., dtype=np.float32)`. Esto permite que la CPU dedique el 100% de sus ciclos al procesamiento de la IA (`torch.no_grad()`) sin sufrir cuellos de botella por deserialización de red.
* **Telemetría Nativa:** Tras realizar la limpieza del buffer del procesador (`cpu_percent(interval=None)`), el Worker evalúa su consumo exacto de RAM y CPU y empaqueta la respuesta en la estructura `BatchResponse`.

## Protocolo: Desacoplamiento de Transporte y Serialización

Esta arquitectura demuestra un principio fundamental de ingeniería en sistemas distribuidos MLOps: **la separación de responsabilidades**.

* **Capa de Transporte (TCP Crudo / ZeroMQ):** Se encarga exclusivamente de mover los bytes con la latencia más baja posible, sin cabeceras HTTP y sin negociación de rutas.
* **Capa de Serialización (Protobuf):** Garantiza que ambos extremos hablen el mismo "idioma" binario, conservando el tipado fuerte sin requerir el pesado motor de red original de Google.

## Despliegue con Ansible

Para la construcción de la imagen, la inyección de código se optimiza. Al no requerir el motor de red de gRPC, el despliegue es más directo.

```bash
# Desplegar inyectando la ruta de ZeroMQ + Protobuf
ansible-playbook -i inventory.ini playbook.yml -e "experimento_path=../2-src-protocols/03-zeromq-protobuf"
```

---

## Guía de Ejecución: Clúster Edge MNIST (ZMQ + Protobuf)

### 1. Preparación del Entorno (Master)

El nodo central requiere las librerías científicas, pyzmq y la generación del traductor binario a partir del `.proto`.

```bash
# 1. Instalar dependencias necesarias
pip install pyzmq protobuf numpy psutil torch torchvision matplotlib seaborn scikit-learn

# 2. Compilar el contrato de datos (Nota: Solo generamos _pb2.py, omitimos grpc_out)
python3 -m grpc_tools.protoc -I. --python_out=. mnist.proto
```

### 2. Despliegue de Infraestructura (Ansible)

Asegúrate de inyectar la variable de ruta para que Ansible tome los archivos de la carpeta correspondiente a esta implementación.

```bash
# 1. Limpieza de contenedores previos
ansible-playbook -i inventory.ini clean.yml

# 2. Despliegue de la imagen de ZeroMQ
ansible-playbook -i inventory.ini playbook.yml -e "experimento_path=../2-src-protocols/03-zeromq-protobuf"
```

### 3. Verificación en los Nodos (Workers)

Conéctate por SSH a los nodos Edge para validar que el servicio de Systemd está levantado y el socket de ZMQ está a la escucha de peticiones.

```bash
# Conectarse al nodo
ssh littledragon@192.168.98.143

# Ver el estado del servicio gestionado por Systemd
systemctl --user status worker.service

# Ver logs (debe indicar "Iniciando Worker Edge IA (ZeroMQ/Protobuf) en puerto 8000...")
journalctl --user -u worker.service -f
```

### 4. Ejecución del Experimento (Master)

Con los Workers listos, ejecuta el archivo principal en la máquina de control para iniciar el entrenamiento, distribuir el modelo e inyectar los arrays a través del túnel TCP multiparte. 

```bash
python master.py
```