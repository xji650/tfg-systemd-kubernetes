# Arquitectura de Orquestación Edge: Implementación ZeroMQ + MessagePack

Este directorio documenta la variante optimizada de la arquitectura basada en TCP crudo. Tras evaluar Protobuf, esta implementación sustituye el tipado estricto por **MessagePack**, un formato de serialización binaria *schema-less* (sin esquema). Esta combinación busca el equilibrio perfecto: la velocidad de red de ZeroMQ, el rendimiento de la serialización binaria y la flexibilidad de desarrollo de los diccionarios nativos de Python.

## 1. Diseño de la Arquitectura (Master-Worker)

El sistema mantiene el patrón de mensajería síncrona Request-Reply (REQ-REP) de ZeroMQ, pero simplifica drásticamente la estructura de los datos transmitidos.

### El Nodo Orquestador (Master)
El orquestador inyecta los datos a través de sockets TCP prescindiendo de compiladores externos:

* **Estructuración Dinámica:** A diferencia de Protobuf, que requiere instanciar clases precompiladas, el Master empaqueta los metadatos y el tensor binario (`particion_np.tobytes()`) directamente en un diccionario estándar de Python.
* **Serialización MessagePack:** Se utiliza `msgpack.packb(..., use_bin_type=True)` para comprimir el diccionario a un formato binario altamente eficiente antes de inyectarlo en el socket `zmq.REQ`.
* **Resiliencia y Concurrencia:** Mantiene el `ThreadPoolExecutor` para la transmisión paralela y la inyección de la directiva de *timeout* (`zmq.RCVTIMEO`) para proteger al orquestador frente a la desconexión abrupta de los nodos Edge.

### Los Nodos Perimetrales (Workers)
Los contenedores *rootless* mantienen el bucle de escucha asíncrono en el puerto 8000, incorporando defensas a nivel de memoria:

* **Desbordamiento de Límites (Buffer Limits):** Por defecto, las librerías de MessagePack imponen límites estrictos de seguridad para prevenir ataques de agotamiento de memoria (OOM). Dado que el payload de visión artificial supera los 94 MB, el Worker sobrescribe explícitamente estos límites durante la deserialización mediante los parámetros `max_bin_len=200*1024*1024` y `max_str_len=200*1024*1024`.
* **Zero-Copy Sostenido:** Tras desempaquetar el diccionario, el Worker recupera el acceso al tensor mediante la clave dinámica (`request['image_data']`) y aplica la técnica de copia cero (`np.frombuffer`) para asignar el bloque de memoria RAM directamente a la CPU.
* **Telemetría y Control de Errores:** Se mide el esfuerzo computacional real ($T_{proc}$, RAM y CPU) aislando el PID. Además, esta variante implementa un bloque `try/except` que captura cualquier error de deserialización y devuelve un estado de `ERROR` encapsulado en MessagePack, garantizando que el clúster no colapse ante paquetes corruptos.

## 2. Análisis del Protocolo: Flexibilidad vs. Contratos Estrictos

Esta implementación representa el extremo opuesto a gRPC en términos de filosofía de desarrollo. Mientras gRPC prioriza la robustez mediante contratos, esta variante prioriza la **agilidad operativa**:

* **Capa de Transporte (TCP Crudo):** Al operar sobre sockets TCP puros gestionados por ZeroMQ, eliminamos la capa de abstracción HTTP/2, reduciendo la negociación de cabeceras y el *handshake* complejo, lo cual es óptimo para comunicaciones de baja latencia en redes privadas.
* **Capa de Serialización (MessagePack):** El uso de un formato *schema-less* elimina el acoplamiento rígido entre cliente y servidor. Esto permite una iteración rápida del modelo de datos sin la sobrecarga de generar y compilar *stubs* de red.

**Ventajas operativas de esta arquitectura:**

* **Desacoplamiento total del ecosistema gRPC:** Al eliminar la dependencia de `grpcio-tools` y los archivos `.proto`, se reduce significativamente la complejidad del `Dockerfile` y el tiempo de *build* de la imagen de contenedor.
* **Minimización de la superficie de ataque:** El despliegue en los nodos Edge depende exclusivamente de dos librerías ligeras (`pyzmq` y `msgpack`), lo que minimiza el tamaño de la imagen base y simplifica las auditorías de seguridad del clúster.

## 3. Despliegue con Ansible

La provisión del entorno inyecta la ruta de este protocolo específico. Al no requerir fase de compilación interna, el *build* de Podman orquestado por Systemd es significativamente más rápido.

```bash
# Desplegar inyectando la ruta de ZMQ+MsgPack para sobrescribir el valor por defecto
ansible-playbook -i inventory.ini playbook.yml -e "experimento_path=../2-src-protocols/04-zeromq-msgpack"
```

---

## Guía de Ejecución: Clúster Edge MNIST (ZMQ + MessagePack)

```bash
# Instalar dependencias necesarias (¡Sin necesidad de compilar nada!)
pip install pyzmq msgpack numpy psutil tensorflow-datasets

# Ejecutar nodo Master
python master.py
```
