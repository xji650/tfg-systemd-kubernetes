## 1. Descripción del Entorno
Este proyecto implementa una arquitectura de procesamiento paralelo bajo el modelo **Master-Worker**. El sistema permite la distribución de carga de visión artificial (dataset MNIST) sobre nodos perimetrales (Edge) orquestados mediante **Ansible** y gestionados localmente por **systemd Quadlets**.

| Componente | Servicio | Puerto (Host) | Protocolo | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| **Worker (Hijos)** | FastAPI / Uvicorn | `8000` | TCP | Recepción de particiones de datos (POST) |

## 4. Dependencias del Software

### Nodo Maestro (Control Machine)
* **Python 3.10+**
* **Librerías:**
    * `tensorflow-datasets`: Ingesta de datos.
    * `numpy`: Preprocesamiento y serialización.
    * `requests`: Cliente HTTP para distribución.

### Nodos Hijos (Edge Workers)
* **Imagen Base:** `python:3.11-slim`
* **Librerías internas (dentro del contenedor):**
    * `fastapi`: Framework de API.
    * `uvicorn`: Servidor ASGI.

## 5. Resultados

### Test 1
```
==================================================
 RESULTADOS DE LA COMPARATIVA TÉCNICA 
==================================================
Protocolo de Comunicación:     HTTP/REST (JSON)
Tiempo Total (s):              17.87 s
Throughput (img/s):            3357.91 img/s
RAM Máx. Worker (MB):          2621.75 MB
CPU Promedio (%):              8.40 %
Datos Totales Red (MB):        242.29 MB
Tasa Éxito (%):                100.00 %
==================================================
```

```
nodo-a

Apr 30 21:43:26 node-a worker-mnist-node-a[2958]: Procesadas 30000 imágenes. RAM: 2641.60MB, CPU: 8.4%
Apr 30 21:43:26 node-a worker-mnist-node-a[2958]: INFO:     10.89.0.2:58350 - "POST /procesar HTTP/1.1" 200 OK
```

```
nodo-b

Apr 30 21:43:26 node-b worker-mnist-node-b[3131]: Procesadas 30000 imágenes. RAM: 2601.90MB, CPU: 8.4%
Apr 30 21:43:26 node-b worker-mnist-node-b[3131]: INFO:     10.89.0.2:44780 - "POST /procesar HTTP/1.1" 200 OK
```

### Test 2
```
==================================================
 RESULTADOS DE LA COMPARATIVA TÉCNICA 
==================================================
Protocolo de Comunicación:     HTTP/REST (JSON)
Tiempo Total (s):              13.39 s
Throughput (img/s):            4482.42 img/s
RAM Máx. Worker (MB):          2631.48 MB
CPU Promedio (%):              1.05 %
Datos Totales Red (MB):        242.29 MB
Tasa Éxito (%):                100.00 %
==================================================
```

```
nodo-a

Apr 30 21:51:11 node-a worker-mnist-node-a[2958]: Procesadas 30000 imágenes. RAM: 2641.68MB, CPU: 1.1%
Apr 30 21:51:11 node-a worker-mnist-node-a[2958]: INFO:     10.89.0.2:55360 - "POST /procesar HTTP/1.1" 200 OK
```

```
nodo-b

Apr 30 21:51:10 node-b worker-mnist-node-b[3131]: Procesadas 30000 imágenes. RAM: 2621.28MB, CPU: 1.0%
Apr 30 21:51:10 node-b worker-mnist-node-b[3131]: INFO:     10.89.0.2:44718 - "POST /procesar HTTP/1.1" 200 OK
```


### Test 3
```
==================================================
 RESULTADOS DE LA COMPARATIVA TÉCNICA 
==================================================
Protocolo de Comunicación:     HTTP/REST (JSON)
Tiempo Total (s):              11.60 s
Throughput (img/s):            5170.64 img/s
RAM Máx. Worker (MB):          2631.48 MB
CPU Promedio (%):              1.50 %
Datos Totales Red (MB):        242.29 MB
Tasa Éxito (%):                100.00 %
==================================================
```

```
nodo-a

Apr 30 21:55:22 node-a worker-mnist-node-a[2958]: Procesadas 30000 imágenes. RAM: 2641.27MB, CPU: 1.5%
Apr 30 21:55:22 node-a worker-mnist-node-a[2958]: INFO:     10.89.0.2:35544 - "POST /procesar HTTP/1.1" 200 OK
```

```
nodo-b

Apr 30 21:55:22 node-b worker-mnist-node-b[3131]: Procesadas 30000 imágenes. RAM: 2621.69MB, CPU: 1.5%
Apr 30 21:55:22 node-b worker-mnist-node-b[3131]: INFO:     10.89.0.2:43806 - "POST /procesar HTTP/1.1" 200 OK
```

### Test 4
```
==================================================
 RESULTADOS DE LA COMPARATIVA TÉCNICA 
==================================================
Protocolo de Comunicación:     HTTP/REST (JSON)
Tiempo Total (s):              12.41 s
Throughput (img/s):            4833.97 img/s
RAM Máx. Worker (MB):          2631.64 MB
CPU Promedio (%):              0.40 %
Datos Totales Red (MB):        242.29 MB
Tasa Éxito (%):                100.00 %
==================================================
```

```
nodo-a

Apr 30 22:33:45 node-a worker-mnist-node-a[2958]: Procesadas 30000 imágenes. RAM: 2642.14MB, CPU: 0.4%
Apr 30 22:33:45 node-a worker-mnist-node-a[2958]: INFO:     10.89.0.2:39638 - "POST /procesar HTTP/1.1" 200 OK
```

```
nodo-b

Apr 30 22:33:45 node-b worker-mnist-node-b[3131]: Procesadas 30000 imágenes. RAM: 2621.14MB, CPU: 0.4%
Apr 30 22:33:45 node-b worker-mnist-node-b[3131]: INFO:     10.89.0.2:38946 - "POST /procesar HTTP/1.1" 200 OK
```

### Test 5
```
==================================================
 RESULTADOS DE LA COMPARATIVA TÉCNICA 
==================================================
Protocolo de Comunicación:     HTTP/REST (JSON)
Tiempo Total (s):              11.38 s
Throughput (img/s):            5274.69 img/s
RAM Máx. Worker (MB):          2631.59 MB
CPU Promedio (%):              4.65 %
Datos Totales Red (MB):        242.29 MB
Tasa Éxito (%):                100.00 %
==================================================
```

```
nodo-a

Apr 30 22:35:01 node-a worker-mnist-node-a[2958]: Procesadas 30000 imágenes. RAM: 2641.62MB, CPU: 4.7%
Apr 30 22:35:01 node-a worker-mnist-node-a[2958]: INFO:     10.89.0.2:36558 - "POST /procesar HTTP/1.1" 200 OK
```

```
nodo-b

Apr 30 22:35:01 node-b worker-mnist-node-b[3131]: Procesadas 30000 imágenes. RAM: 2621.56MB, CPU: 4.6%
Apr 30 22:35:01 node-b worker-mnist-node-b[3131]: INFO:     10.89.0.2:35192 - "POST /procesar HTTP/1.1" 200 OK
```