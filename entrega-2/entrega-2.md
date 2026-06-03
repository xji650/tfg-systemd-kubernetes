# Orchestration Trade-offs in Edge Computing: systemd vs Kubernetes

Edge environments challenge conventional cloud-native orchestration models due to limited resources and simplified deployment requirements. This work analyzes the trade-offs between Kubernetes and systemd as orchestration solutions for edge nodes. Using a set of representative workloads and fault-injection experiments, the study evaluates performance, resilience, and management complexity, offering design insights for selecting appropriate orchestration mechanisms in edge computing scenarios.

---

# Informe de Seguimiento: Comparativa de Systemd + podman

![Podman](https://img.shields.io/badge/Podman-Rootless-892CA0?style=flat-square&logo=podman)
![Systemd](https://img.shields.io/badge/Systemd-Orchestration-darkgreen?style=flat-square&logo=linux)
![Paradigma](https://img.shields.io/badge/JSON_vs_Binary-Architecture-red?style=flat-square)

El objetivo de esta entrega consiste en hacer la comparativa de diferentes protocolos de comunicaciones en Systemd + podman para una misma tarea y obtener las metricas y números.

La tarea consiste en:

    Amb el datset MNIST (https://www.tensorflow.org/datasets/catalog/mnist), has de fer:
    1. Aquest datset s'ha de separar en N parts, que s'enviaran als N nodes fills

    2. Els nodes fills faran una tasca sobre aquest dataset. Comença fent que la tasca sigui comptar el nombre d'imatges que li arriben al fill

    3. Els nodes fills han de retornar al pare el resultat de la tasca. En aquest cas aquest nombre d'imatges

``` mermaid
flowchart TD
Internet((Internet))

subgraph Maquina1 [Máquina 1: Master / Padre]
    direction TB
    Ansible[Plano de Control:\nAnsible Playbooks]
    Padre[Plano de Datos:\nContenedor Padre Podman]
    
    Ansible -. "Fase1 Configura a sí mismo\n(Quadlets, systemd)" .-> Padre
end

subgraph Maquina2 [Máquina 2: Worker 1]
    Hijo1[Contenedor Hijo 1]
end

subgraph Maquina3 [Máquina 3: Worker 2]
    Hijo2[Contenedor Hijo 2]
end

%% FASE 1: Aprovisionamiento (Ansible a Hijos)
Ansible -- "Fase1 SSH: Configura y arranca" --> Hijo1
Ansible -- "Fase1 SSH: Configura y arranca" --> Hijo2

%% FASE 2: Dataset
Internet -- "Fase2 Descarga MNIST" --> Padre

%% FASE 3 y 4: Procesamiento (Protocolos a evaluar)
Padre -- "Fase3 Envía fragmentos \n(HTTP, gRPC, MQTT...)" --> Hijo1
Hijo1 -- "Fase4 Recibe resultados\n(HTTP, gRPC, MQTT...)" --> Padre

Padre -- "Fase3 Envía fragmentos \n(HTTP, gRPC, MQTT...)" --> Hijo2
Hijo2 -- "Fase4 Recibe resultados\n(HTTP, gRPC, MQTT...)" --> Padre


%% Estilos
classDef control fill:#f3e5f5,stroke:#8e24aa,stroke-width:2px;
classDef datos fill:#e1f5fe,stroke:#039be5,stroke-width:2px;
classDef worker fill:#f1f8e9,stroke:#689f38,stroke-width:2px;

class Ansible control;
class Padre datos;
class Hijo1,Hijo2 worker;

```

---

## Índice
1. Resumen Ejecutivo
2. Infraesrtructura
3. Resumen de Fases del trabajo
4. Comparativa protocolos de comunicación
5. Métricas evaluadas
6. Resultados de la Evaluación Técnica
7. Análisis y Conclusiones

---

## 1. Resumen Ejecutivo
Tras la consolidación de la infraestructura base orquestada mediante systemd, esta fase del proyecto se ha centrado en evaluar la viabilidad de la comunicación de datos masivos en el Edge. 

Se implementó inicialmente un sistema basado en el estándar web (**HTTP/REST con JSON**) que reveló severos cuellos de botella en memoria y latencia. 

Esto motivó un cambio de paradigma arquitectónico hacia la **serialización binaria**, implementando y comparando dos soluciones avanzadas: **gRPC (sobre HTTP/2)**, **ZeroMQ (sobre TCP crudo, P2P)** y **MQTT (pub-sub)**. 

Simultáneamente, se ha refactorizado el despliegue con Ansible para soportar estas tres arquitecturas de forma modular.

---

## 2. Especificaciones de Infraestructura
- **Entorno**: 
    - Maquina virtual vmware con 2 nodos worker/hijos ubuntu 24.04.4 
    - un nodo master/padre en ubuntu 22.04.5 en Windows 11 via wsl 
* **Orquestador de Despliegue:** Ansible 2.10+ en nodo master 
* **Gestor de Contenedores:** Podman 4.5+ (Modo Rootless)
* **Supervisor de Servicios:** systemd 
* **Dataset:** TensorFlow Datasets (MNIST - 60,000 imágenes de entrenamiento)

---

## 3. Resumen de fases del trabajo y del desarollo

### Fase 1: Aprovisionamiento y Control (Ansible)

- Mecanismo: SSH.

- Acción: El nodo máster se conecta por SSH a los workers, despliega los archivos Quadlet, hace el systemctl daemon-reload y levanta los servicios.

### Fase 2: Fase 2: Obtención del Dataset (Nodo Padre)
- Mecanismo: HTTP.

- Acción: Nodo Master hace una petición HTTPS (usando curl, wget o librerías de Python/Node) para descargar el archivo comprimido del MNIST al disco local del contenedor una sola vez. Luego, lo carga en memoria, lo divide en **N** partes y lo deja listo para la Fase 3.

### Fase 3: Procesamiento y Distribución (Padre -> Hijos)
- Mecanismo: Comparativa. El envío se hace mediante el stack de red de los contenedores (Podman) usando los diferentes protocolos de comunicación.

- Acción: El nodo master manda las imágenes procesados a los nodos worker mediante http, mqtt, grpc, zeromq, amqp... y con correspondiente formato como texto json, binario(protobuf, messaje pack...)

    - HTTP/REST transportando JSON (Lento pero estándar ¿base64?).

    - gRPC transportando Protobuf (Rápido y binario).

    - MQTT / ZeroMQ transportando MessagePack o BSON (Asíncrono y ligero).

    - AMQP (...)

### Fase 4: Retorno de Resultados (Hijos -> Padre)

Nodos hijos genera reporte de las metricas y resultados y lo devuelve al nodo padre usando los mismos protocolos de comunicación que el envío.

Así es como funcionaría el retorno según el protocolo activo:

- Si la Fase 3 usa HTTP/REST: El Padre hizo una petición POST al Hijo. El Hijo procesa las imágenes y, en la misma conexión, devuelve un HTTP 200 OK con el JSON de respuesta: {"conteo": 35000, "worker_id": 1}.

- Si la Fase 3 usa gRPC: El Padre abre un Stream o hace un Unary Call. Cuando el Hijo termina su función, simplemente devuelve el objeto definido en tu archivo .proto y la librería gRPC se encarga de enviarlo de vuelta por el túnel HTTP/2.

- Si la Fase 3 usa MQTT/AMQP: Aquí es un poco diferente porque es asíncrono. Se utiliza el patrón Request-Reply.

    - El Padre publica las imágenes en un topic llamado tareas/worker1.

    - El Padre se queda suscrito a un topic llamado respuestas/worker1.

    - El Hijo lee la tarea, cuenta las imágenes y publica el resultado final en respuestas/worker1.

- Si la fase 3 usa gRPC...

---

## 3. Implementación Técnica y Orquestación

El sistema Master-Worker distribuye dinámicamente particiones del dataset MNIST según la fórmula:
$$tamano\_particion = \frac{total\_imagenes}{N\_nodos}$$

Para acomodar la evaluación de las tres arquitecturas, el pipeline de **Ansible** se ha rediseñado bajo el principio de separación entre *Build* y *Run*:
*   **Aprovisionamiento Agnóstico:** El orquestador inyecta configuraciones Quadlet idénticas para los contenedores *rootless*, independientemente de si ejecutan FastAPI (REST), un *Servicer* (gRPC) o un *Socket REP* (ZeroMQ).
*   **Compilación Centralizada:** Para los protocolos binarios, el archivo de interfaz (`.proto`) se compila en el nodo Master. Ansible distribuye el código precompilado a los nodos Edge, evitando instalar pesadas herramientas de compilación (`grpcio-tools`) en los contenedores perimetrales y reduciendo su huella de almacenamiento.

---

## 4. Comparativa y experimento

#### Comparativa de protocolo 
HTTP/v1.1 + json
HTTP/2 + binario - protobuf (gRPC)
ZeroMQ + binario - protobuf
MQTT + binario - protobuf

#### Comparativa de formato de envio de datos
ZeroMQ + binario - protobuf
ZeroMq + binario - Messaje Pack


### 1. La Línea Base (El estándar a batir)

* **Prueba:** `HTTP/1.1 + JSON`
* **Por qué:** Es obligatorio tenerlo. Necesitas demostrar empíricamente lo ineficiente que es enviar texto plano con cabeceras pesadas en un entorno *Edge*. Sin esta gráfica lenta y costosa en CPU, las mejoras de los otros protocolos no destacarán en tu memoria del proyecto.

### 2. El Estándar Moderno de Microservicios

* **Prueba:** `gRPC (HTTP/2 + Protobuf)`
* **Por qué:** Es el ciudadano de primera clase en Kubernetes. Medir su rendimiento casi perfecto en Systemd te dará un contraste brutal cuando lo midas más adelante en K3s y veas cuánto penaliza la capa de red virtual (CNI) de Kubernetes a las conexiones persistentes.

### 3. El Rendimiento Crudo (Brokerless)

* **Prueba:** `ZeroMQ + Protobuf`
* **Por qué:** Representa el límite físico de la máquina. Al no haber un servidor intermedio (broker), mides la velocidad extrema de nodo a nodo. En un TFG sobre orquestación, esto te permite aislar y medir el rendimiento del *stack* de red de Podman en estado puro.

### 4. El Estándar Edge / IoT (Con Broker)

* **Prueba:** `MQTT + Protobuf`
* **Por qué:** Al introducir un *broker* intermedio (Mosquitto), podrás medir cuánta latencia y memoria RAM extra consume tener un intermediario gestionando colas, algo vital en arquitecturas descentralizadas. Protobuf asegura que la red mueva el paquete más ligero posible.

### 5. La "Batalla" de la Serialización

* **Prueba:** `ZeroMQ + MessagePack` **O BIEN** `MQTT + MessagePack` *(Elige solo una de las dos).*
* **Por qué:** En lugar de probar MessagePack en *todos* los protocolos, hazlo solo en uno (por ejemplo, en MQTT). Esto te permite tener una sección específica en tu TFG llamada: *"Impacto de la serialización con esquema (Protobuf) vs. sin esquema (MessagePack)"*. Mantienes el protocolo de red estático y mides si la comodidad de programar con MessagePack justifica el ligero aumento de latencia frente a Protobuf.

---

### El Cambio de Paradigma: De Texto Plano (JSON) a Binario

*   **El Cuello de Botella (JSON):** En la implementación HTTP/REST, transmitir tensores matemáticos obligaba a convertir matrices a listas nativas y serializarlas como texto plano. Al recibir el *payload*, el nodo Worker colapsaba su memoria RAM intentando parsear el gigantesco archivo de texto para reconstruir los diccionarios en memoria antes de poder procesar la información.
*   **La Solución Binaria (Protobuf):** Para solventar esto, se adoptó *Protocol Buffers*. Este enfoque permite empaquetar los datos en crudo (`bytes`). Al llegar al nodo, se utiliza una técnica de *zero-parsing* (`np.frombuffer`), volcando los bytes directamente a la memoria de la CPU sin intermediarios lógicos, lo que libera drásticamente los recursos del sistema.

---

### Resumen visual de tu arquitectura de pruebas final:

| Enfoque Arquitectónico | Protocolo de Red | Serialización | Objetivo en el TFG |
| --- | --- | --- | --- |
| **Tradicional** | HTTP/1.1 | JSON | Demostrar el *overhead* máximo (Línea base). |
| **RPC Moderno** | gRPC | Protobuf | Evaluar el estándar corporativo y de K8s. |
| **Directo (Brokerless)** | ZeroMQ | Protobuf | Medir el rendimiento de red crudo (Podman puro). |
| **Asíncrono (IoT)** | MQTT | Protobuf | Medir la penalización del *Broker* en el *Edge*. |
| **Flexibilidad vs Rigidez** | MQTT *(o ZMQ)* | MessagePack | Comparar el coste de no usar contratos precompilados. |

---

## 5. Métricas evaluadas

--- 

## 6. Resultados de la Evaluación Técnica

Se han realizado pruebas de estrés enviando un lote continuo de 60.000 imágenes (aprox. 94 MB) a los nodos Edge. La siguiente tabla refleja la media consolidada de 5 ejecuciones independientes:

| Métrica Evaluada | Fase 1: HTTP/REST (JSON) | Fase 2: gRPC (Protobuf) | Fase 3: ZeroMQ (Protobuf) |
| :--- | :--- | :--- | :--- |
| **Tiempo Total (s)** | 13,33 s | 0,67 s | **0,35 s** |
| **Throughput (img/s)** | ~4.623 img/s | ~89.338 img/s | **~171.578 img/s** |
| **Consumo RAM Máx.** | **2.631,48 MB** *(Crítico)* | 275,46 MB | 300,57 MB |
| **Uso CPU Promedio** | 3,20% *(Bloqueo I/O)* | 49,44% | 50,00% |
| **Datos Transmitidos** | 242,29 MB | **179,44 MB** | **179,44 MB** |

## 7. Análisis y Conclusiones

La evolución a través de las tres arquitecturas arroja conclusiones claras para el diseño de sistemas Edge:
1.  **La Inviabilidad de REST/JSON:** El consumo de más de 2.6 GB de RAM para leer un mensaje demuestra que las APIs web tradicionales no son aptas para la transmisión de datos densos en dispositivos perimetrales limitados.
2.  **El Impacto de la Serialización:** Migrar de JSON a Protobuf eliminó más de 60 MB de basura sintáctica en la red y redujo el consumo de RAM en un 89%, permitiendo a la CPU trabajar libre de bloqueos de E/S.
3.  **Transporte TCP vs HTTP/2:** Una vez resuelto el problema de la serialización con Protobuf, la comparativa de transporte demostró que eliminar las capas HTTP (gRPC) para bajar a sockets TCP puros (ZeroMQ) duplica el rendimiento, logrando tiempos de 0.35 segundos.

Todo ello demuestra que la optimización de los protocolos de red es tan crítica como la propia orquestación de los contenedores mediante **systemd**, logrando un sistema ultraligero y de alto rendimiento.
