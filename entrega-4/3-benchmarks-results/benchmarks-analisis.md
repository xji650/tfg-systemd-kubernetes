# Análisis de Resultados y Benchmarking

Este documento consolida la evaluación técnica de las cuatro iteraciones arquitectónicas desarrolladas para el procesamiento distribuido de visión artificial en el Edge bajo **Kubernetes (K3s)**. Los datos expuestos representan la **media histórica total** de las pruebas de estrés, extraídas automáticamente del Data Lake (`resultados_globales.csv`).

## 1. Metodología de Medición (Híbrida)

Para garantizar la validez científica y la equidad en la comparativa de la infraestructura, se ha diseñado una estrategia de medición híbrida que separa el consumo de la plataforma del consumo de la IA:

* **Medición en Reposo (Global / OS-Level):** El consumo de CPU y RAM antes de inyectar carga se captura a nivel del sistema operativo completo mediante comandos nativos (`free -m` y `vmstat`) ejecutados vía SSH.
    > Medir únicamente el contenedor oculta el verdadero "Impuesto Arquitectónico" (*Architectural Overhead*). K3s requiere ejecutar demonios pesados en segundo plano (kubelet, containerd, flannel). Medir a nivel global es la única forma de exponer que el orquestador reserva ~850 MB de RAM solo por mantener el clúster vivo en un dispositivo perimetral.

* **Medición bajo Estrés (Aislamiento PID):** Durante la inferencia, la telemetría (RAM Máx y CPU Máx) se recolecta aislando el proceso interno del contenedor (`psutil.Process(os.getpid())`).
    > Esto evita que los picos de red o los demonios de Kubernetes contaminen los datos de estrés, midiendo exclusivamente el esfuerzo computacional de la serialización y la predicción matemática del protocolo evaluado.

### Anomalías Esperadas

* **Consumo de CPU (>100%):** En entornos multihilo, las lecturas representan la suma de la utilización de todos los núcleos asignados al proceso. Valores de ~190% indican que el proceso Worker está saturando casi 2 núcleos de cómputo de manera efectiva.

* **Resiliencia (MTTR):** El Tiempo Medio de Recuperación (*Mean Time To Recovery*) en K3s promedia ~1.6 segundos para regenerar un Pod destruido abruptamente y ponerlo en estado `Ready`. Se observa una anomalía de ~53s en la media histórica de MessagePack, atribuible a un *Cold Start* o reasignación de red (flannel) durante el *Chaos Testing* en K3s.

---

## 2. Baseline: HTTP/REST (JSON)

La implementación basada en el estándar web tradicional (HTTP/1.1 y JSON) establece la línea de referencia.

* **Penalización de Red (Payload):** Al no soportar transmisión binaria nativa, las matrices de píxeles se convierten a texto, inflando el *payload* de red a **15.59 MB** por lote de imágenes.

* **Cuello de Botella Híbrido:** La latencia de red (RTT) supera el medio segundo (**516.90 ms**) y el tiempo de procesamiento en el Worker ($T_{proc}$) ronda los **503.45 ms**. La ineficiencia radica tanto en el transporte HTTP como en el pesado *parsing* asíncrono necesario para reconstruir el JSON antes de la inferencia.

### 2.1. Tabla métricas HTTP/REST (JSON)

| Métrica Consolidada | HTTP/REST (JSON) |
| --- | --- |
| **Tiempo Total Promedio** | 0.99 s |
| **Throughput Promedio** | 2086.61 img/s |
| **Latencia RTT Promedio** | 516.90 ms |
| **Tiempo $T_{proc}$ Promedio** | 503.45 ms |
| **Pico Máximo RAM (Worker)** | 337.30 MB |
| **CPU Promedio (Worker)** | 138.94 % |
| **Datos Totales Red** | 15.59 MB por nodo |

---

## 3. Evolución a serialización binaria: 

### 3.1. gRPC, Protobuf y Zero-Copy

La migración hacia gRPC introduce la serialización binaria y la multiplexación sobre HTTP/2, resolviendo los problemas críticos de ancho de banda del *baseline*.

* **Eficiencia de Carga Útil:** El *payload* se reduce a su peso matemático en bytes puros (**2.99 MB**), ahorrando más de 12 MB de sobrecarga por transmisión.

* **Aceleración Computacional:** Al recibir datos binarios pre-tipados, el $T_{proc}$ se desploma de 503 ms a **281.93 ms**, disparando el rendimiento global a **6358.87 img/s** y demostrando el poder del *Zero-Copy parsing*.

### Tabla métricas gRPC (Protobuf)

| Métrica Consolidada | gRPC (Protobuf) |
| --- | --- |
| **Tiempo Total Promedio** | 0.33 s |
| **Throughput Promedio** | 6358.87 img/s |
| **Latencia RTT Promedio** | 319.32 ms |
| **Tiempo $T_{proc}$ Promedio** | 281.93 ms |
| **Pico Máximo RAM (Worker)** | 392.79 MB |
| **CPU Promedio (Worker)** | 186.82 % |
| **Datos Totales Red** | 2.99 MB por nodo |

---

### 3.2. ZeroMQ y Transporte TCP Crudo

En esta fase, se mantiene el contrato binario de Protobuf pero se descarta el pesado motor de red de Google (HTTP/2) en favor de sockets TCP directos mediante ZeroMQ.

* **Máxima Velocidad Física:** Al eliminar la negociación de cabeceras HTTP de la capa de aplicación, la latencia RTT cae a su mínimo histórico: **263.85 ms**.

* **Rendimiento Máximo Absoluto:** El $T_{proc}$ desciende a **201.72 ms**, permitiendo a la CPU centrarse en el tensor de PyTorch. Esta arquitectura se corona como la más rápida de la comparativa, superando las **7033 img/s**.

### Tabla métricas ZeroMQ (Protobuf)

| Métrica Consolidada | ZeroMQ (Protobuf) |
| --- | --- |
| **Tiempo Total Promedio** | 0.31 s |
| **Throughput Promedio** | 7033.38 img/s |
| **Latencia RTT Promedio** | 263.85 ms |
| **Tiempo $T_{proc}$ Promedio** | 201.72 ms |
| **Pico Máximo RAM (Worker)** | 282.18 MB |
| **CPU Promedio (Worker)** | 194.28 % |
| **Datos Totales Red** | 2.99 MB por nodo |

---

### 3.3. ZeroMQ + MessagePack 

La iteración final sustituye los contratos estrictos de Protobuf por **MessagePack**, un empaquetador binario dinámico sin esquemas, buscando la flexibilidad del JSON pero con la compresión del nivel C.

* **Máxima Eficiencia de Memoria RAM:** Al evitar la instanciación de clases generadas por compiladores externos (`_pb2`), la huella máxima de RAM del proceso Worker se estabiliza en **275.12 MB**, siendo la arquitectura más ligera en consumo de recursos de las tres opciones binarias.
* **Competitividad Extrema:** Aunque cede un marginal 6% en Throughput frente a Protobuf (**6555.69 img/s**), mantiene el RTT en unos extraordinarios **277.54 ms**, logrando un equilibrio perfecto.

### Tabla métricas ZeroMQ (MessagePack)

| Métrica Consolidada | ZeroMQ (MessagePack) |
| --- | --- |
| **Tiempo Total Promedio** | 0.33 s |
| **Throughput Promedio** | 6555.69 img/s |
| **Latencia RTT Promedio** | 277.54 ms |
| **Tiempo $T_{proc}$ Promedio** | 203.35 ms |
| **Pico Máximo RAM (Worker)** | 275.12 MB |
| **CPU Promedio (Worker)** | 196.35 % |
| **Datos Totales Red** | 2.99 MB por nodo |

---

## 4. Análisis Visual Comparativo

A continuación, se presentan las métricas clave extraídas tras el procesamiento del *Data Lake*. Estas gráficas ilustran la evolución del rendimiento desde el baseline (HTTP/JSON) hasta las arquitecturas optimizadas de ZeroMQ.

### 4.1. Throughput: Evolución por Protocolo

*Esta gráfica demuestra la escalabilidad del sistema al eliminar el overhead de red y serialización.*

![Gráfica de Throughput](./visualizations/graph_1_throughput.png)

> **Observación:** Se aprecia un salto exponencial superior al 300% en el rendimiento al migrar de protocolos basados en texto (JSON) a binarios, alcanzando el pico absoluto con ZeroMQ y Protobuf.

### 4.2. Consumo de Memoria (RAM): Reposo Global vs. Estrés Aislado

*Comparativa del footprint de memoria en el entorno Edge.*

![Gráfica de Consumo RAM](./visualizations/graph_2_ram_footprint.png)

> **Observación:** Las métricas de Reposo (columnas azul claro) reflejan el peso fijo de la arquitectura Kubernetes (~850 MB), independiente del protocolo. Durante el Estrés (columnas azul oscuro), se demuestra que MessagePack y Protobuf logran estabilizar el consumo de la IA, evitando el ahogo de memoria que provoca la deserialización asíncrona de gRPC y HTTP.

### 4.3. Matriz de Trade-off (Latencia vs. Rendimiento)

*Relación entre la latencia de red (RTT) y la capacidad de procesamiento (Throughput).*

![Gráfica de Trade-off](./visualizations/graph_3_scatter_tradeoff.png)

> **Observación:** El cuadrante superior izquierdo (Baja latencia, Alto throughput) es dominado por las soluciones de ZeroMQ. gRPC queda como una solución intermedia sólida, mientras que HTTP/JSON queda totalmente aislado en el cuadrante de peor desempeño.

---

## 5. Conclusión y Trade-Offs

El análisis estadístico evidencia que **los estándares web tradicionales (HTTP/JSON) son inviables para el procesamiento de tensores masivos en el Edge**, generando cuellos de botella severos tanto en ancho de banda como en ciclos de CPU.

### 1. **La serialización binaria es innegociable:** 
El salto de HTTP a cualquier alternativa binaria comprimió el *payload* de red de ~15 MB a ~3 MB, reduciendo la latencia RTT casi a la mitad y triplicando el rendimiento base.

### 2. **El "Impuesto Arquitectónico" es real:** 
K3s penaliza los dispositivos perimetrales con un consumo en vacío de ~850 MB de RAM. Cuando se opera en nodos de 4 GB o menos, elegir el protocolo correcto a nivel de proceso determina si el clúster sobrevive o colapsa por falta de memoria (OOM).

### 3. **Trade-off Final (Rendimiento vs Mantenibilidad):**
* **ZeroMQ + Protobuf** es la opción elegida si se busca la victoria absoluta en rendimiento bruto (**7033 img/s**).

* **ZeroMQ + MessagePack** se consolida como la arquitectura MLOps óptima en el mundo real. Cede un margen insignificante de velocidad (**6555 img/s**), pero erradica la dependencia de compiladores estrictos y genera el menor impacto de RAM bajo estrés de todas las soluciones binarias evaluadas.