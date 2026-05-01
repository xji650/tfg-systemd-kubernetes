Para que tu TFG sea reproducible y profesional, el **README** debe contener los comandos exactos para que cualquier persona (o el tribunal) pueda levantar el sistema desde cero.

Aquí tienes la estructura de comandos organizada por fases, utilizando los archivos de configuración que ya tienes definidos.

---

## 🚀 Guía de Ejecución: Clúster Edge MNIST (gRPC)

### 1. Preparación del Entorno (Master)
Antes de nada, necesitas generar el código de gRPC a partir del contrato `.proto`.
```bash
# Instalar dependencias necesarias
pip install grpcio grpcio-tools psutil numpy

# Compilar el contrato (Genera los archivos _pb2.py)
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. mnist.proto
```

### 2. Despliegue de Infraestructura (Ansible)
Usa el inventario de tus nodos para configurar Podman, la red interna y los Quadlets de Systemd.
```bash
# 1. Limpiar cualquier rastro previo (Opcional)
ansible-playbook -i inventory.ini cleanup.yml

# 2. Desplegar y arrancar el clúster
ansible-playbook -i inventory.ini deploy.yml
```

### 3. Verificación en los Nodos (Workers)
Si quieres comprobar que los contenedores están corriendo bajo Systemd sin root en `node-a` o `node-b`:
```bash
# Conectarse al nodo
ssh littledragon@192.168.98.143

# Ver el estado del servicio gestionado por Systemd
systemctl --user status worker.service

# Ver logs en tiempo real del servidor gRPC
journalctl --user -u worker.service -f
```

### 4. Ejecución del Experimento (Master)
Una vez que los Workers están en `running`, lanza el script principal para obtener la tabla de resultados.
```bash
python master.py
```

---

## 🛠 Comandos de Mantenimiento

### Actualización de Código
Si modificas el `worker.py`, solo tienes que relanzar el playbook. Ansible se encarga de:
1. Copiar los archivos nuevos.
2. Reconstruir la imagen con `podman build`.
3. Reiniciar el servicio con `systemctl --user restart`.
```bash
ansible-playbook -i inventory.ini deploy.yml
```

### Limpieza Total
Para dejar los nodos (`node-a` y `node-b`) como si nada hubiera pasado, eliminando imágenes, redes y servicios:
```bash
ansible-playbook -i inventory.ini cleanup.yml
```

---

### Notas para la Memoria
*   **Persistencia:** Se utiliza `loginctl enable-linger` para que los contenedores no se apaguen al cerrar la sesión SSH.
*   **Orquestación Nativa:** No hay Docker Daemon; Systemd gestiona directamente el ciclo de vida de los procesos a través de Quadlets.
*   **Comunicación:** El flujo gRPC utiliza el puerto `8000` expuesto en cada nodo para la transmisión binaria de datos.

---

## 5. Resultados

### Test 1
```
==================================================
 RESULTADOS DE LA COMPARATIVA TÉCNICA 
==================================================
Protocolo de Comunicación:     gRPC (Protobuf/Binary)
Tiempo Total (s):              0.80 s
Throughput (img/s):            74761.07 img/s
RAM Máx. Worker (MB):          259.49 MB
CPU Promedio (%):              50.75 %
Datos Totales Red (MB):        179.44 MB
Tasa Éxito (%):                100.00 %
==================================================
```

```
nodo-a

May 01 01:40:50 node-a worker-mnist-node-a[11435]: gRPC: Procesadas 30000 imágenes. RAM: 270.11MB, CPU: 44.4%
```

```
nodo-b

May 01 01:40:49 node-b worker-mnist-node-b[11562]: gRPC: Procesadas 30000 imágenes. RAM: 248.87MB, CPU: 57.1%
```

### Test 2
```
==================================================
 RESULTADOS DE LA COMPARATIVA TÉCNICA 
==================================================
Protocolo de Comunicación:     gRPC (Protobuf/Binary)
Tiempo Total (s):              0.66 s
Throughput (img/s):            90470.43 img/s
RAM Máx. Worker (MB):          281.43 MB
CPU Promedio (%):              43.65 %
Datos Totales Red (MB):        179.44 MB
Tasa Éxito (%):                100.00 %
==================================================
```

```
nodo-a

May 01 01:44:29 node-a worker-mnist-node-a[11435]: gRPC: Procesadas 30000 imágenes. RAM: 288.02MB, CPU: 44.4%
```

```
nodo-b

May 01 01:44:29 node-b worker-mnist-node-b[11562]: gRPC: Procesadas 30000 imágenes. RAM: 274.84MB, CPU: 42.9%
```


### Test 3
```
==================================================
 RESULTADOS DE LA COMPARATIVA TÉCNICA 
==================================================
Protocolo de Comunicación:     gRPC (Protobuf/Binary)
Tiempo Total (s):              0.65 s
Throughput (img/s):            92710.45 img/s
RAM Máx. Worker (MB):          280.72 MB
CPU Promedio (%):              50.00 %
Datos Totales Red (MB):        179.44 MB
Tasa Éxito (%):                100.00 %
==================================================
```

```
nodo-a

May 01 01:45:42 node-a worker-mnist-node-a[11435]: gRPC: Procesadas 30000 imágenes. RAM: 283.78MB, CPU: 55.6%
```

```
nodo-b

May 01 01:45:42 node-b worker-mnist-node-b[11562]: gRPC: Procesadas 30000 imágenes. RAM: 277.66MB, CPU: 44.4%
```

### Test 4
```
==================================================
 RESULTADOS DE LA COMPARATIVA TÉCNICA 
==================================================
Protocolo de Comunicación:     gRPC (Protobuf/Binary)
Tiempo Total (s):              0.62 s
Throughput (img/s):            96571.41 img/s
RAM Máx. Worker (MB):          276.25 MB
CPU Promedio (%):              52.80 %
Datos Totales Red (MB):        179.44 MB
Tasa Éxito (%):                100.00 %
==================================================
```

```
nodo-a

May 01 01:46:42 node-a worker-mnist-node-a[11435]: gRPC: Procesadas 30000 imágenes. RAM: 276.89MB, CPU: 50.0%
```

```
nodo-b
May 01 01:46:42 node-b worker-mnist-node-b[11562]: gRPC: Procesadas 30000 imágenes. RAM: 275.60MB, CPU: 55.6%
```

### Test 5
```
==================================================
 RESULTADOS DE LA COMPARATIVA TÉCNICA 
==================================================
Protocolo de Comunicación:     gRPC (Protobuf/Binary)
Tiempo Total (s):              0.65 s
Throughput (img/s):            92177.85 img/s
RAM Máx. Worker (MB):          279.43 MB
CPU Promedio (%):              50.00 %
Datos Totales Red (MB):        179.44 MB
Tasa Éxito (%):                100.00 %
==================================================
```

```
nodo-a

May 01 01:47:34 node-a worker-mnist-node-a[11435]: gRPC: Procesadas 30000 imágenes. RAM: 281.33MB, CPU: 50.0%
```

```
nodo-b

May 01 01:47:34 node-b worker-mnist-node-b[11562]: gRPC: Procesadas 30000 imágenes. RAM: 277.52MB, CPU: 50.0%
```