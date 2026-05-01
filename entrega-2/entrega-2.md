# Orchestration Trade-offs in Edge Computing: systemd vs Kubernetes

Edge environments challenge conventional cloud-native orchestration models due to limited resources and simplified deployment requirements. This work analyzes the trade-offs between Kubernetes and systemd as orchestration solutions for edge nodes. Using a set of representative workloads and fault-injection experiments, the study evaluates performance, resilience, and management complexity, offering design insights for selecting appropriate orchestration mechanisms in edge computing scenarios.

---

# Informe de Seguimiento: Evolución de Protocolos y el Paradigma Binario en el Edge

![Podman](https://img.shields.io/badge/Podman-Rootless-892CA0?style=flat-square&logo=podman)
![Systemd](https://img.shields.io/badge/Systemd-Orchestration-darkgreen?style=flat-square&logo=linux)
![Paradigma](https://img.shields.io/badge/JSON_vs_Binary-Architecture-red?style=flat-square)

---

## 1. Resumen Ejecutivo
Tras la consolidación de la infraestructura base orquestada mediante systemd, esta fase del proyecto se ha centrado en evaluar la viabilidad de la comunicación de datos masivos en el Edge. Se implementó inicialmente un sistema basado en el estándar web (**HTTP/REST con JSON**) que reveló severos cuellos de botella en memoria y latencia. Esto motivó un cambio de paradigma arquitectónico hacia la **serialización binaria**, implementando y comparando dos soluciones avanzadas: **gRPC (sobre HTTP/2)** y **ZeroMQ (sobre TCP crudo)**. Simultáneamente, se ha refactorizado el despliegue con Ansible para soportar estas tres arquitecturas de forma modular.

## 2. El Cambio de Paradigma: De Texto Plano (JSON) a Binario
El hallazgo más crítico de esta fase ha sido la demostración empírica de que los estándares web tradicionales son ineficientes para cargas de IA en el Edge:
*   **El Cuello de Botella (JSON):** En la implementación HTTP/REST, transmitir tensores matemáticos obligaba a convertir matrices a listas nativas y serializarlas como texto plano. Al recibir el *payload*, el nodo Worker colapsaba su memoria RAM intentando parsear el gigantesco archivo de texto para reconstruir los diccionarios en memoria antes de poder procesar la información.
*   **La Solución Binaria (Protobuf):** Para solventar esto, se adoptó *Protocol Buffers*. Este enfoque permite empaquetar los datos en crudo (`bytes`). Al llegar al nodo, se utiliza una técnica de *zero-parsing* (`np.frombuffer`), volcando los bytes directamente a la memoria de la CPU sin intermediarios lógicos, lo que libera drásticamente los recursos del sistema.

## 3. Implementación Técnica y Orquestación

El sistema Master-Worker distribuye dinámicamente particiones del dataset MNIST según la fórmula:
$$tamano\_particion = \frac{total\_imagenes}{N\_nodos}$$

Para acomodar la evaluación de las tres arquitecturas, el pipeline de **Ansible** se ha rediseñado bajo el principio de separación entre *Build* y *Run*:
*   **Aprovisionamiento Agnóstico:** El orquestador inyecta configuraciones Quadlet idénticas para los contenedores *rootless*, independientemente de si ejecutan FastAPI (REST), un *Servicer* (gRPC) o un *Socket REP* (ZeroMQ).
*   **Compilación Centralizada:** Para los protocolos binarios, el archivo de interfaz (`.proto`) se compila en el nodo Master. Ansible distribuye el código precompilado a los nodos Edge, evitando instalar pesadas herramientas de compilación (`grpcio-tools`) en los contenedores perimetrales y reduciendo su huella de almacenamiento.

## 4. Resultados de la Evaluación Técnica

Se han realizado pruebas de estrés enviando un lote continuo de 60.000 imágenes (aprox. 94 MB) a los nodos Edge. La siguiente tabla refleja la media consolidada de 5 ejecuciones independientes:

| Métrica Evaluada | Fase 1: HTTP/REST (JSON) | Fase 2: gRPC (Protobuf) | Fase 3: ZeroMQ (Protobuf) |
| :--- | :--- | :--- | :--- |
| **Tiempo Total (s)** | 13,33 s | 0,67 s | **0,35 s** |
| **Throughput (img/s)** | ~4.623 img/s | ~89.338 img/s | **~171.578 img/s** |
| **Consumo RAM Máx.** | **2.631,48 MB** *(Crítico)* | 275,46 MB | 300,57 MB |
| **Uso CPU Promedio** | 3,20% *(Bloqueo I/O)* | 49,44% | 50,00% |
| **Datos Transmitidos** | 242,29 MB | **179,44 MB** | **179,44 MB** |

## 5. Análisis y Conclusiones
La evolución a través de las tres arquitecturas arroja conclusiones claras para el diseño de sistemas Edge:
1.  **La Inviabilidad de REST/JSON:** El consumo de más de 2.6 GB de RAM para leer un mensaje demuestra que las APIs web tradicionales no son aptas para la transmisión de datos densos en dispositivos perimetrales limitados.
2.  **El Impacto de la Serialización:** Migrar de JSON a Protobuf eliminó más de 60 MB de basura sintáctica en la red y redujo el consumo de RAM en un 89%, permitiendo a la CPU trabajar libre de bloqueos de E/S.
3.  **Transporte TCP vs HTTP/2:** Una vez resuelto el problema de la serialización con Protobuf, la comparativa de transporte demostró que eliminar las capas HTTP (gRPC) para bajar a sockets TCP puros (ZeroMQ) duplica el rendimiento, logrando tiempos de 0.35 segundos.

Todo ello demuestra que la optimización de los protocolos de red es tan crítica como la propia orquestación de los contenedores mediante **systemd**, logrando un sistema ultraligero y de alto rendimiento.
