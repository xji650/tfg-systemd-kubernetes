# Pasos para la ejecución 

## 1. Descripción del Entorno
Este proyecto implementa una arquitectura de procesamiento paralelo bajo el modelo **Master-Worker**. El sistema permite la distribución de carga de visión artificial (dataset MNIST) sobre nodos perimetrales (Edge) orquestados mediante **Ansible** y gestionados localmente por **systemd Quadlets**.

## 2. Especificaciones de Infraestructura
* **Orquestador de Despliegue:** Ansible 2.10+
* **Gestor de Contenedores:** Podman 4.5+ (Modo Rootless)
* **Supervisor de Servicios:** systemd (User Session)
* **Comunicación:** Protocolo HTTP (REST)
* **Dataset:** TensorFlow Datasets (MNIST - 60,000 imágenes de entrenamiento)

## 3. Matriz de Conectividad y Puertos
El sistema requiere la apertura de los siguientes puertos en los nodos para garantizar la comunicación entre el Nodo Pare y los Nodos Fill:

| Componente | Servicio | Puerto (Host) | Protocolo | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| **Worker (Hijos)** | FastAPI / Uvicorn | `8000` | TCP | Recepción de particiones de datos (POST) |
| **Balanceador** | Nginx | `8888` | TCP | Punto de entrada único para el clúster |
| **SSH** | OpenSSH Server | `22` | TCP | Gestión y despliegue con Ansible |

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

## 5. Procedimiento de Instalación y Despliegue

### Paso 1: Configuración de Claves SSH
Se requiere intercambio de claves RSA para permitir la ejecución desatendida de Ansible:
```bash
ssh-keygen -t rsa -b 4096
ssh-copy-id -i ~/.ssh/id_rsa.pub user@<ip-nodo>
```

### Paso 2: Aprovisionamiento (Ansible)
El despliegue automatiza la habilitación de **Linger**, la creación de la red virtual Quadlet y el build local de la imagen de aplicación:
```bash
ansible-playbook -i inventory.ini playbook.yml -K
```

### Paso 3: Ejecución del Reparto de Carga
Desde la máquina de control, se inicia la partición y envío de datos:
```bash
python master.py
```

### Opcional: Monitorización de logs
Monitorización de Logs:
```Bash
journalctl --user -u worker.service -f
```

## 6. Limpieza del Entorno
Para revertir todos los cambios, eliminar imágenes construidas y redes virtuales:

```Bash
ansible-playbook -i inventory.ini clean.yml -K
```

## 7. Arquitectura de Resiliencia (systemd)
La robustez del sistema se basa en la integración nativa de Podman con systemd a través de **Quadlets** (`.container` files).

* **Restart Policy:** `always` con un `RestartSec=3`. Si el proceso de cálculo satura la memoria o el contenedor falla, systemd garantiza el reinicio sin intervención manual.
* **Network Isolation:** Cada worker se integra en una red aislada (`red.network`) definida de forma declarativa, evitando colisiones con otros servicios del host.
* **Persistence:** El estado de los servicios se mantiene activo tras reinicios del hardware mediante la persistencia del gestor de servicios de usuario (`loginctl enable-linger`).

## 8. Monitorización y Telemetría
Para auditoría técnica de los nodos en tiempo real, se utilizan las herramientas estándar de Linux:

* **Estado del Servicio:** `systemctl --user status worker.service`
* **Logs de Aplicación:** `journalctl --user -u worker.service -f --since "1 hour ago"`
* **Consumo de Recursos:** `podman stats`

## 9. Enlaces y Referencias
* **Dataset Source:** [TensorFlow Datasets - MNIST](https://www.tensorflow.org/datasets/catalog/mnist)
* **Documentación Quadlet:** [Podman Quadlet Guide](https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html)
* **Ansible Systemd Module:** [Community.General.Systemd](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/systemd_module.html)


```
ansible all -i inventory.ini -m shell -a "ip route add default via 192.168.0.1" -b -K
```