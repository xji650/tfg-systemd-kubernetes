# Arquitectura de Orquestación Edge: Implementación ZeroMQ

Este directorio documenta la tercera versión de la comparativa de protocolos de red para arquitecturas distribuidas en entornos Edge Computing. Tras validar la eficiencia de la serialización binaria con Protobuf, esta fase abandona por completo el estándar HTTP (incluyendo HTTP/2 de gRPC) para operar directamente sobre la capa de transporte TCP mediante **ZeroMQ (ZMQ)**, logrando el máximo rendimiento y la menor latencia posible.

## 1. Diseño de la Arquitectura (Master-Worker)

El sistema implementa el patrón de mensajería síncrona Request-Reply (REQ-REP) característico de ZeroMQ, manteniendo el tipado estricto de los datos.

### El Nodo Orquestador (Master)
El script central actúa como cliente de red puro, inyectando los datos directamente a través de sockets TCP:

* **Concurrencia ZMQ:** A diferencia de las peticiones HTTP convencionales, el Master instancia un `zmq.Context()` y utiliza sockets de tipo `zmq.REQ` dentro de un `ThreadPoolExecutor` para establecer túneles de comunicación directa con cada IP del clúster.
* **Gestión de Resiliencia:** Puesto que ZeroMQ es un protocolo de muy bajo nivel que no implementa *timeouts* por defecto para operaciones de bloqueo, se ha inyectado la directiva `socket.setsockopt(zmq.RCVTIMEO, 300000)` a nivel de socket para evitar cuelgues infinitos ante la posible caída de un nodo Edge.
* **Empaquetado Binario:** Se reutiliza el contrato Protobuf (`BatchRequest`) para serializar los arrays `float32` de NumPy, transformándolos en una cadena de bytes pura (`SerializeToString()`) antes de iniciar el cronómetro de RTT.
* **Aislamiento de Métricas:** El tiempo de tránsito y procesamiento se mide estrictamente mediante relojes de alta resolución (`time.perf_counter()`), aislando las métricas de red del propio esfuerzo de empaquetado del orquestador.

### Los Nodos Perimetrales (Workers)
Los contenedores *rootless* ejecutan un bucle de escucha asíncrono gestionado nativamente por la librería `pyzmq`.

* **Socket Bind (REP):** El servidor mapea un socket `zmq.REP` al puerto `8000`, eliminando el *overhead* de los servidores web tradicionales (como Uvicorn) o los pesados *servicers* de gRPC.
* **Zero-Parsing en RAM:** Al igual que en la fase anterior, los datos recibidos (`message_bytes`) se procesan usando la estructura Protobuf (`ParseFromString()`) y el tensor se mapea instantáneamente en memoria utilizando `np.frombuffer`. Esta técnica permite que la CPU procese las imágenes sin cuellos de botella de I/O por deserialización.
* **Telemetría Nativa:** Tras realizar la limpieza del buffer del procesador (`cpu_percent(interval=None)`), el Worker evalúa su consumo exacto de RAM y CPU mediante `psutil` y empaqueta la respuesta en la estructura Protobuf `BatchResponse` para enviarla de vuelta por el túnel TCP.

## 2. Protocolo: Desacoplamiento de Transporte y Serialización

Esta arquitectura demuestra un principio fundamental de ingeniería en sistemas distribuidos: **la separación de responsabilidades**.

* **Capa de Transporte (TCP Crudo / ZeroMQ):** Se encarga exclusivamente de mover los bytes del punto A al punto B con la latencia más baja posible, sin cabeceras HTTP, sin negociación de rutas y sin sobrecargas innecesarias para una red de área local (LAN).
* **Capa de Serialización (Protobuf):** Se mantiene la definición de la interfaz (`mnist.proto`), garantizando que ambos extremos hablen el mismo "idioma" binario, conservando el tipado fuerte y la compresión sin requerir el motor de red original de Google.

## 3. Despliegue con Ansible (Optimización)

Para la construcción de la imagen en Podman, se ha optimizado la inyección de código. Al no requerir el motor de red de gRPC, el comando de compilación del contrato omite la directiva `--grpc_python_out=.`.

```bash
# Desplegar inyectando la ruta de ZeroMQ para sobrescribir el valor por defecto
ansible-playbook -i inventory.ini playbook.yml -e "experimento_path=../2-src-protocols/03-zeromq-proto"
```

---

## Guía de Ejecución: Clúster Edge MNIST (ZeroMQ)

```bash
# Instalar dependencias necesarias
pip install pyzmq protobuf numpy psutil tensorflow-datasets

# Compilar el contrato de datos (Solo generamos _pb2.py, omitimos _pb2_grpc.py)
python3 -m grpc_tools.protoc -I. --python_out=. mnist.proto

# Ejecutar nodo Master
python master.py
```