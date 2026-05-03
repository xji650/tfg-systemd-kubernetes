# Arquitectura de Orquestación Edge: Implementación ZeroMQ

Este repositorio documenta la tercera versión de la comparativa de protocolos para arquitecturas distribuidas en entornos Edge Computing. Tras validar la eficiencia de la serialización binaria con Protobuf, esta fase abandona por completo el estándar HTTP (incluyendo HTTP/2 de gRPC) para operar directamente sobre la capa de transporte TCP mediante **ZeroMQ (ZMQ)**, logrando el máximo rendimiento posible.

---
## 1. Diseño de la Arquitectura (Master-Worker)

El sistema implementa el patrón de mensajería síncrona Request-Reply (REQ-REP) característico de ZeroMQ, manteniendo el tipado estricto de los datos.

### **El Nodo Orquestador (Master)**
El script central actúa como cliente de red puro, inyectando los datos directamente a través de sockets TCP:
*   **Concurrencia ZMQ:** A diferencia de las peticiones HTTP convencionales, el Master instancia un `zmq.Context()` y utiliza sockets de tipo `zmq.REQ` dentro de un `ThreadPoolExecutor` para establecer túneles de comunicación directa con cada IP del clúster.
*   **Gestión de Resiliencia:** Puesto que ZeroMQ es un protocolo de muy bajo nivel que no implementa *timeouts* por defecto para operaciones de bloqueo, se ha inyectado la directiva `socket.setsockopt(zmq.RCVTIMEO, 300000)` a nivel de socket para evitar cuelgues infinitos ante la posible caída de un nodo Edge.
*   **Empaquetado Binario:** Se reutiliza el contrato Protobuf (`BatchRequest`) para serializar los arrays `float32` de NumPy, transformándolos en una cadena de bytes pura (`SerializeToString()`).

### **Los Nodos Perimetrales (Workers)**
Los contenedores *rootless* ejecutan un bucle de escucha asíncrono gestionado nativamente por la librería `pyzmq`.
*   **Socket Bind (REP):** El servidor mapea un socket `zmq.REP` al puerto `8000`, eliminando el *overhead* de los servidores web tradicionales (como Uvicorn) o los *servicer* de gRPC.
*   **Zero-Parsing en RAM:** Al igual que en gRPC, los datos recibidos (`message_bytes`) se deserializan e inyectan instantáneamente en memoria utilizando `np.frombuffer`, permitiendo que la CPU procese los tensores sin cuellos de botella de I/O.
*   **Telemetría Nativa:** Tras el procesamiento, el Worker evalúa su consumo de RAM y CPU mediante `psutil` y empaqueta la respuesta en la estructura Protobuf `BatchResponse`.

---
## 2. Protocolo: Desacoplamiento de Transporte y Serialización

Esta arquitectura demuestra un principio fundamental de ingeniería: **la separación de responsabilidades**.
*   **Capa de Transporte (TCP Crudo / ZeroMQ):** Se encarga exclusivamente de mover los bytes del punto A al punto B con la latencia más baja posible, sin cabeceras HTTP, sin negociación de rutas y sin encriptación innecesaria para una LAN privada.
*   **Capa de Serialización (Protobuf):** Se mantiene la definición de la interfaz (`mnist.proto`), garantizando que ambos extremos hablen el mismo "idioma" binario sin requerir el motor de red original de Google.

---
## 3. Despliegue con Ansible (Optimización)

Para la construcción de la imagen en Podman, se ha optimizado el `Dockerfile`. Al no requerir el motor de red de gRPC, el comando de compilación del contrato omite la directiva `--grpc_python_out=.`. 
```dockerfile
# Solo se generan las clases de datos de Protobuf, descartando el código muerto de red HTTP/2
RUN python -m grpc_tools.protoc -I. --python_out=. mnist.proto
```

---
## 4. Análisis de Rendimiento (resultados en `experiments.md`)

Las métricas demuestran que ZeroMQ es el ganador indiscutible en rendimiento puro, superando tanto al estándar REST/JSON como a la implementación gRPC.

*   **Rendimiento Absoluto (Throughput):** El tiempo de procesamiento total cae a **0.35 segundos**, logrando un Throughput que supera las 171.000 imágenes por segundo. Esto representa el doble de velocidad que gRPC y es **37 veces más rápido que HTTP/REST**.
*   **Consumo de RAM Estable:** El uso máximo de memoria en los Workers se mantiene en el umbral altamente eficiente de ~300 MB, confirmando que la serialización binaria es la solución al problema de saturación de RAM de JSON.
*   **Maximización de CPU:** Al eliminar la capa HTTP/2, los datos llegan a la RAM a una velocidad tal que la CPU se mantiene en un uso constante e intenso (~50%), evidenciando una arquitectura libre de cuellos de botella de E/S.

### 4.1. RESULTADOS: ZeroMQ (Protobuf/Binary)

| Prueba | Tiempo Total (s) | Throughput (img/s) | RAM Máx, Worker (MB) | CPU Promedio (%) | Datos Totales Red (MB) | Tasa Éxito (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Test 1** | 0,34 | 178893,75 | 300,56 MB | 50,00% | 179,44 MB | 100,00% |
| **Test 2** | 0,41 | 147392,58 | 300,57 MB | 50,00% | 179,44 MB | 100,00% |
| **Test 3** | 0,33 | 182602,66 | 300,57 MB | 52,80% | 179,44 MB | 100,00% |
| **Test 4** | 0,31 | 191235,91 | 300,57 MB | 47,20% | 179,44 MB | 100,00% |
| **Test 5** | 0,38 | 157765,91 | 300,58 MB | 50,00% | 179,44 MB | 100,00% |
| **Total** | **0,354** | **171578,16** | **300,57 MB** | **50,00%** | **179,44 MB** | **100,00%** |


### **4.2. ANÁLISIS Build-in vs. Save/Load**

Se ha realizado una comparativa técnica entre dos modelos de despliegue para el protocolo **ZeroMQ (Protobuf/Binary)** con el fin de validar si la distribución de imágenes pre-construidas (*Save/Load*) afecta al rendimiento de la lógica de negocio en comparación con la compilación directa en el nodo (*Build-in*).

### 1) Resumen Comparativo de Ejecución (Runtime)

A continuación, se presenta la media de los resultados obtenidos en ambos experimentos una vez alcanzado el **estado estacionario** (tras la estabilización del sistema):

| Métrica de Ejecución | Experimento 1 (Build-in) | Experimento 2 (Save/Load) | Diferencia |
| :--- | :--- | :--- | :--- |
| **Tiempo Total Promedio (s)** | 0.354 s | 0.350 s* | -1.13% |
| **Throughput (img/s)** | 171,578.16 | 172,579.41* | +0.58% |
| **RAM Máx. Worker (MB)** | 300.57 MB | 300.53 MB | -0.01% |
| **CPU Promedio (%)** | 50.00 % | 50.96 % | +1.92% |
| **Tasa de Éxito (%)** | 100.00 % | 100.00 % | 0.00% |

*\*Calculado sobre los tests de estabilidad (Tests 3, 4 y 5 del segundo experimento).*

### 2) Discusión de los Resultados

#### A. Equivalencia de Rendimiento (Steady State)
Los datos demuestran que, una vez que el contenedor está en ejecución y las librerías han sido cargadas en la memoria caché del sistema operativo, **no existe una penalización de rendimiento** por utilizar el método *Save/Load*. La latencia de procesamiento de imágenes se mantiene en el rango de los **0.33s - 0.35s**, lo que garantiza que el tiempo es independiente del método de despliegue utilizado.

#### B. Fenómeno de Latencia Transitoria (Warm-up)
Se ha identificado que en el Experimento 2 (*Save/Load*), los primeros tests tras el despliegue presentan una latencia superior (~0.68s). Este fenómeno se atribuye al **I/O Wait** del sistema de archivos de la Raspberry Pi, que continúa gestionando el volcado de datos de la imagen OCI a la memoria física inmediatamente después de la carga del artefacto `.tar`. Este comportamiento es transitorio y desaparece tras las primeras ráfagas de ejecución.

#### C. Justificación de la Arquitectura Final
Aunque ambos métodos ofrecen el mismo rendimiento de trabajo, se selecciona el modelo **Save/Load** como la arquitectura definitiva por las siguientes ventajas de ingeniería:
1.  **Determinismo:** Se garantiza que todos los nodos ejecutan un binario idéntico bit a bit, eliminando discrepancias por versiones de dependencias durante la compilación.
2.  **Protección de Recursos:** Al eliminar la fase de `build` en el worker, se evitan picos de temperatura y consumo de RAM que podrían comprometer la estabilidad del hardware perimetral.
3.  **Capacidad Air-Gapped:** El sistema es capaz de desplegarse en entornos sin acceso a internet, una condición crítica para vehículos en movimiento.

---

## 🚀 Guía de Ejecución: Clúster Edge MNIST (ZeroMQ)

### 1. Preparación del Entorno (Master)
El nodo central requiere la librería de ZeroMQ y la generación del traductor binario a partir del `.proto`.
```bash
# Instalar dependencias necesarias
pip3 install pyzmq protobuf numpy psutil tensorflow-datasets

# Compilar el contrato de datos (Solo generamos _pb2.py, omitimos _pb2_grpc.py)
python3 -m grpc_tools.protoc -I. --python_out=. mnist.proto
```

### 2. Despliegue de Infraestructura (Ansible)
Asegúrate de que el inventario apunta a la ruta de ZeroMQ (`experimento_path: "../results/zeromq"`). A continuación, despliega los Quadlets en los Workers.
```bash
# 1. Limpieza de contenedores previos (Obligatorio al cambiar de red)
ansible-playbook -i inventory_3.ini clean_3.yml

# 2. Despliegue de la imagen optimizada de ZeroMQ
ansible-playbook -i inventory_3.ini playbook_3.yml
```

### 3. Verificación en los Nodos (Workers)
Conéctate por SSH a los nodos Edge para validar que el servicio de Systemd está levantado y el socket de ZMQ está a la escucha de peticiones crudas.
```bash
# Conectarse al nodo
ssh littledragon@192.168.98.143

# Ver logs en tiempo real del contenedor
journalctl --user -u worker.service -f
```

### 4. Ejecución del Experimento (Master)
Con los Workers listos, ejecuta el archivo principal en la máquina de control para inyectar los arrays a través del túnel TCP.
```bash
python3 master.py
```