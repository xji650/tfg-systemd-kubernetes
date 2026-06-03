## Protocolos de comunicación

### Tipos de protocolos de comunicación

Para entender los protocolos de comunicación, la mejor analogía es pensar en el envío de paquetes físicos: si el formato de datos (JSON, Protobuf) es la **caja** que contiene el producto, el protocolo de comunicación es la **carretera y el tipo de vehículo** (camión, avión, moto) que lo transporta.

En la arquitectura de software moderna, no solemos clasificar los protocolos por su capa OSI (capa de red, transporte, etc.), sino por **su patrón de comportamiento y el problema arquitectónico que resuelven**.

Aquí tienes las 4 grandes familias de protocolos de comunicación:

---

### 1. La Familia Síncrona 

#### Petición - Respuesta (Request-Response)

Es el modelo clásico: el cliente hace una petición, espera en la línea, y el servidor responde.

* **HTTP/1.1:** El estándar fundacional de la web (REST APIs). Abre una conexión, envía texto plano (cabeceras), recibe la respuesta y cierra (o mantiene viva la conexión un tiempo).
  * *Cuándo usarlo:* APIs públicas tradicionales, navegadores, servicios que no requieren alta velocidad.

* **HTTP/2 y HTTP/3:** La evolución del protocolo web. HTTP/2 introduce la "multiplexación" (enviar múltiples peticiones simultáneas por un solo tubo TCP) y comprime las cabeceras en binario. HTTP/3 va más allá y abandona TCP para usar QUIC (basado en UDP), eliminando los cuellos de botella de red inestable.
  * *Cuándo usarlo:* APIs modernas, microservicios, conexiones web de alto rendimiento.
  
* **gRPC (Remote Procedure Call):** Construido directamente sobre HTTP/2. En lugar de usar URLs clásicas como `/api/usuarios`, llamas a funciones de otro servidor como si fueran código local: `getUsuario(1)`. Por defecto usa Protobuf.
  * *Cuándo usarlo:* Comunicación estricta y rapidísima de *backend a backend*.

#### Tiempo Real Bidireccional (Streaming Abierto)

Para cuando necesitas que el servidor empuje información al cliente de forma constante, sin que el cliente tenga que preguntar continuamente si hay datos nuevos (*polling*).

* **WebSockets:** Abre un túnel TCP persistente y bidireccional entre cliente y servidor. Ambos pueden enviarse mensajes en cualquier momento con muy baja latencia.
  * *Cuándo usarlo:* Chats en vivo, juegos multijugador de navegador, dashboards de telemetría en tiempo real.
* **WebRTC:** Diseñado para comunicación *Peer-to-Peer* (P2P). Permite que dos clientes (ej. navegadores) se conecten directamente entre sí sin pasar los datos pesados por un servidor central.
  * *Cuándo usarlo:* Videollamadas, transferencia directa de archivos.
* **SSE (Server-Sent Events):** Es una conexión HTTP/1.1 estándar, pero configurada para que el servidor deje el canal abierto y envíe actualizaciones unidireccionales (Servidor -> Cliente).
  * *Cuándo usarlo:* Notificaciones *push* web, feeds de eventos.

---

### 2. La Familia Asíncrona

#### Orientada a Mensajes y Pub/Sub (Con Broker)

Aquí se rompe la dependencia directa. El que envía los datos (Productor) no habla directamente con el que los recibe (Consumidor). Delegan el mensaje en un intermediario o *Broker*.

* **MQTT:** Diseñado específicamente para redes poco fiables y dispositivos con poca batería o CPU. Utiliza un patrón Publicador/Suscriptor con una sobrecarga (*overhead*) de red minúscula.
  * *Cuándo usarlo:* Telemetría en el *edge*, domótica, recolección de datos de sensores remotos.
* **AMQP (Ej. RabbitMQ):** El protocolo de mensajería para sistemas empresariales pesados. Es complejo pero garantiza que el mensaje no se pierda bajo ninguna circunstancia, soportando enrutamientos lógicos muy avanzados.
  * *Cuándo usarlo:* Sistemas transaccionales, colas de procesamiento de tareas pesadas donde la fiabilidad es crítica.
* **Kafka Protocol:** Optimizado no para colas tradicionales, sino para procesar un flujo continuo de eventos masivos (*Data Streaming*) escribiéndolos en disco de forma secuencial.
  * *Cuándo usarlo:* Ingesta masiva de logs, analítica de datos a gran escala.

#### Red a Bajo Nivel / Alta Frecuencia (Brokerless)

Saltan por encima de los cuellos de botella tradicionales (eliminando el intermediario) para ofrecer latencias ultrabajas.

* **ZeroMQ (ZMQ):** A menudo se describe como "sockets con esteroides". No es un servidor, sino una librería que se integra en el código. Permite patrones de comunicación hiper-rápidos directamente de memoria a memoria (mediante IPC - *Inter-Process Communication*) o a través de la red local. Al no requerir un proxy o enrutador virtual de red complejo, exprime al máximo el rendimiento del hardware.
  * *Cuándo usarlo:* Comunicación extrema de *workers* en un mismo nodo físico, procesamiento de IA local, arquitecturas donde la latencia de red no es aceptable.

---

### Resumen para elegir la combinación correcta:

Tu elección del protocolo dictará qué formato de serialización tiene más sentido en la arquitectura:

1. **API REST Pública:** `HTTP/1.1` + `JSON`
2. **Microservicios Internos:** `gRPC (HTTP/2)` + `Protobuf`
3. **Sensores de baja potencia / IoT:** `MQTT` + `MessagePack` o bytes crudos.
4. **Comunicación ultrarrápida (mismo nodo):** `ZeroMQ` (vía IPC) + `FlatBuffers` o `Protobuf`.







