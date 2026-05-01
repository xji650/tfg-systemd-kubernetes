# Arquitectura de Orquestación Edge: Implementación gRPC

Este repositorio documenta la segunda iteración de la comparativa de protocolos para arquitecturas distribuidas en entornos Edge Computing. En esta fase, se abandona el estándar web tradicional en favor de **gRPC y Protocol Buffers (Protobuf)**, un framework de Comunicación a Procedimiento Remoto (RPC) de alto rendimiento, ideal para la transmisión eficiente de datos binarios masivos.

## Diseño de la Arquitectura (Master-Worker)

El sistema evoluciona hacia un modelo de comunicación basado en contratos estrictos, optimizando tanto el empaquetado de datos como el uso de memoria RAM.

### 1. El Nodo Orquestador (Master)
El script `master.py` actúa como cliente gRPC y distribuidor de la carga de visión artificial.
*   **Conversión Binaria Nativa:** Carga el dataset MNIST y lo convierte a matrices `float32` de NumPy. En lugar de parsear a listas, inyecta los datos directamente en formato binario mediante `particion_np.tobytes()`.
*   **Canales Inseguros Optimizados:** Establece conexiones concurrentes a través de `grpc.insecure_channel` mediante un `ThreadPoolExecutor`. Para soportar el envío de tensores masivos, se sobreescribe el límite nativo de gRPC, configurando `max_send_message_length` a 200 MB.

### 2. Los Nodos Perimetrales (Workers)
Los contenedores *rootless* ejecutan un servidor gRPC instanciado en el puerto 8000.
*   **Servidor RPC:** La clase `MnistServicer` implementa el método `ProcessBatch` definido en el contrato Protobuf.
*   **Zero-Parsing en Memoria:** El Worker recibe el payload binario (`request.image_data`) y lo mapea directamente a un array de NumPy utilizando `np.frombuffer`. Esta técnica elimina la sobrecarga computacional de decodificar texto a variables lógicas.
*   **Telemetría Integrada:** Se inspeccionan los recursos del nodo con `psutil` y se devuelven en un objeto `BatchResponse` fuertemente tipado.

## Protocolo y Formato de Serialización

*   **Capa de Transporte (HTTP/2):** gRPC opera nativamente sobre HTTP/2, permitiendo multiplexación real sobre una única conexión TCP.
*   **Capa de Serialización (Protobuf):** El intercambio de datos se rige por un Interface Definition Language (IDL) en el archivo `mnist.proto`. Esto garantiza un tipado fuerte de las variables (ej. `int32`, `bytes`, `float`) y comprime la transmisión al eliminar la basura sintáctica (llaves, comas, nombres de campos) inherente a JSON.

## Despliegue con Ansible

Los contenedores se construyen a partir de la imagen `python:3.11-slim`. En esta iteración, el `Dockerfile` de los Workers incluye una fase de compilación interna: instala `grpcio-tools` y ejecuta el compilador `protoc` (`RUN python -m grpc_tools.protoc...`) en tiempo de construcción para generar los *stubs* de red (`_pb2.py` y `_pb2_grpc.py`) dentro del clúster.
```yaml
# En el archivo de variables o inventario de Ansible
experimento_path: "../results/grpc"
```

## Análisis de Rendimiento (resultados en `experiments.md`)

Las métricas demuestran una mejora arquitectónica drástica al migrar de serialización de texto a binaria, resolviendo el cuello de botella de memoria detectado en la prueba HTTP/REST.

*   **Aceleración Extrema (Tiempo):** El tiempo de procesamiento de la red entera desciende a un promedio de **0.67 segundos** (frente a los ~13.3s de REST).
*   **Liberación de Memoria (RAM):** Al no tener que crear diccionarios en memoria para parsear JSON, el consumo de RAM de los Workers se desploma, pasando de 2.6 GB a un promedio de **~275 MB**.
*   **Eficiencia de Red:** Protobuf reduce el payload transferido de 242 MB a **179.44 MB**, eliminando 63 MB de *overhead* sintáctico.
*   **Saturación Positiva de CPU:** El uso de CPU sube a un ~49%, lo que indica que el proceso ya no está bloqueado por latencia de red (I/O Bound) y el procesador puede ingerir y procesar la matriz a máxima velocidad.

### RESULTADOS: gRPC (Protobuf/Binary)

| Prueba | Tiempo Total (s) | Throughput (img/s) | RAM Máx, Worker (MB) | CPU Promedio (%) | Datos Totales Red (MB) | Tasa Éxito (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Test 1** | 0,80 | 74761,07 | 259,49 MB | 50,75% | 179,44 MB | 100,00% |
| **Test 2** | 0,66 | 90470,43 | 281,43 MB | 43,65% | 179,44 MB | 100,00% |
| **Test 3** | 0,65 | 92710,45 | 280,72 MB | 50,00% | 179,44 MB | 100,00% |
| **Test 4** | 0,62 | 96571,41 | 276,25 MB | 52,80% | 179,44 MB | 100,00% |
| **Test 5** | 0,65 | 92177,85 | 279,43 MB | 50,00% | 179,44 MB | 100,00% |
| **Total** | **0,676** | **89338,24** | **275,46 MB** | **49,44%** | **179,44 MB** | **100,00%** |

---

## Guía de Ejecución: Clúster Edge MNIST (gRPC)

### 1. Preparación del Entorno (Master)
Antes de nada, necesitas generar el código de gRPC a partir del contrato `.proto`.
```bash
# Instalar dependencias necesarias
pip install grpcio grpcio-tools psutil numpy

# Compilar el contrato (Genera los archivos _pb2.py y _pb2_grpc.py)
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. mnist.proto
```

### 2. Despliegue de Infraestructura (Ansible)
Usa el inventario de tus nodos para configurar Podman, la red interna y los Quadlets de Systemd. Asegúrate de que la ruta del experimento apunte a la carpeta `grpc`.
```bash
# 1. Limpiar cualquier rastro previo de otros protocolos (Opcional pero recomendado)
ansible-playbook -i inventory.ini clean.yml -K

# 2. Desplegar y arrancar el clúster
ansible-playbook -i inventory.ini playbook.yml -K
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
Una vez que los Workers están en `running` y escuchando en el puerto 8000, lanza el script principal para inyectar la carga y obtener la tabla de resultados.
```bash
python master.py
```


## Comandos de Mantenimiento

### Actualización de Código
Si modificas el `worker.py`, solo tienes que relanzar el playbook. Ansible se encarga de:
1. Copiar los archivos nuevos.
2. Reconstruir la imagen con `podman build`.
3. Reiniciar el servicio con `systemctl --user restart`.
```bash
ansible-playbook -i inventory.ini playbook.yml -K
```

### Limpieza Total
Para dejar los nodos (`node-a` y `node-b`) como si nada hubiera pasado, eliminando imágenes, redes y servicios:
```bash
ansible-playbook -i inventory.ini clean.yml -K
```