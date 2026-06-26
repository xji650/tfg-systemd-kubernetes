# Entrega 2

![Podman](https://img.shields.io/badge/Podman-Rootless-892CA0?style=flat-square&logo=podman)
![Systemd](https://img.shields.io/badge/Systemd-Orchestration-darkgreen?style=flat-square&logo=linux)
![Entrega](https://img.shields.io/badge/Entrega-2-blue?style=flat-square)

El objetivo de esta entrega consiste en hacer la comparativa de diferentes protocolos de comunicaciones en Systemd + podman para una misma tarea y obtener las metricas y números.

La tarea consiste en:

    Amb el datset MNIST (https://www.tensorflow.org/datasets/catalog/mnist), has de fer:
    1. Aquest datset s'ha de separar en N parts, que s'enviaran als N nodes fills

    2. Els nodes fills faran una tasca sobre aquest dataset. Comença fent que la tasca sigui comptar el nombre d'imatges que li arriben al fill

    3. Els nodes fills han de retornar al pare el resultat de la tasca. En aquest cas aquest nombre d'imatges

## 1. Descripción del Entorno


## 2. Especificaciones de Infraestructura
* **Orquestador de Despliegue:** Ansible 2.10+
* **Gestor de Contenedores:** Podman 4.5+ (Modo Rootless)
* **Supervisor de Servicios:** systemd (User Session)
* **Dataset:** TensorFlow Datasets (MNIST - 60,000 imágenes de entrenamiento)

## 3. Matriz de Conectividad y Puertos
El sistema requiere la apertura de los siguientes puertos en los nodos para garantizar la comunicación entre el Nodo Pare y los Nodos Fill:

| Componente | Servicio | Puerto (Host) | Protocolo | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| **SSH** | OpenSSH Server | `22` | TCP | Gestión y despliegue con Ansible |


## 4. Procedimiento de Instalación y Despliegue

### Paso 1: Configuración entorno

#### 1. Intercambio de claves RSA

Se requiere intercambio de claves RSA para permitir la ejecución desatendida de Ansible:
```bash
ssh-keygen -t rsa -b 4096
ssh-copy-id -i ~/.ssh/id_rsa.pub user@<ip-nodo>
```

#### 2. Entorno Virtual Python

Para ejecutar este proyecto de forma aislada y segura, es necesario configurar un entorno virtual y descargar las dependencias. Sigue estos pasos desde la raíz del proyecto:

1. **Crear el entorno virtual:**
    ```bash
    python3 -m venv .venv
    ```

2. **Activar el entorno virtual:**
* En Linux o macOS: `source .venv/bin/activate`
* En Windows: `.venv\Scripts\activate`
* *(Sabrás que está activado si ves `(.venv)` al principio de tu línea de comandos).*

3. **Instalar las dependencias requerides:**
    ```bash
    pip install -r requirements.txt
    ```

### Paso 2: Despliegue
El despliegue automatiza la habilitación de **Linger**, la creación de la red virtual Quadlet y el build local de la imagen de aplicación. 

#### Opción A: Despliegue Estándar
Para levantar el clúster de forma normal sin extraer métricas de infraestructura:

```bash 
# 1. Desplegar protocolo

# http-json
ansible-playbook -i inventory.ini playbook.yml

ansible-playbook -i inventory.ini playbook.yml -e "experimento_path=../2-src-protocols/01-http-json"

# grpc-protobuf
ansible-playbook -i inventory.ini playbook.yml -e "experimento_path=../2-src-protocols/02-grpc-protobuf"

# zeromq-protobuf
ansible-playbook -i inventory.ini playbook.yml -e "experimento_path=../2-src-protocols/03-zeromq-protobuf"

# zeromq-messagepack
ansible-playbook -i inventory.ini playbook.yml -e "experimento_path=../2-src-protocols/04-zeromq-messagepack"
```
```bash
# 2. Ejecución del Reparto de Carga desde la máquina de control
python3 master.py
```

#### Opción B: Ejecución Automatizada (Zero-Touch)

Limpieza + Despliegue + Ejecución de nodos

Para extraer los datos del Plano de Gestión ($T_{deploy}$, Consumo en Reposo, $T_{recovery}$), se ejecutará el script de automatización. Este script envuelve la ejecución de Ansible y aplica pruebas de Chaos Engineering sobre los nodos perimetrales:

```bash
# 1. Configurar la clave de administrador local (solo la primera vez)
echo 'ansible_become_pass: "TU_CONTRASEÑA_AQUI"' > group_vars/workers.yml

# 2. Dar permisos de ejecución al pipeline
chmod +x generate_benchmarks.sh

# 3. Lanzar la evaluación global
./generate_benchmarks.sh
```
*(Los resultados de cada arquitectura se guardarán automáticamente en la carpeta `3-benchmarks-results/raw_logs/` del proyecto).*

### Opcional: Monitorización de logs
Monitorización de Logs:
```Bash
journalctl --user -u worker.service -f
```

## 5. Limpieza del Entorno
Para revertir todos los cambios, eliminar imágenes construidas y redes virtuales:

```Bash
ansible-playbook -i inventory.ini clean.yml -K
```

## 6. Arquitectura de Resiliencia (systemd)
La robustez del sistema se basa en la integración nativa de Podman con systemd a través de **Quadlets** (`.container` files).

* **Restart Policy:** `always` con un `RestartSec=3`. Si el proceso de cálculo satura la memoria o el contenedor falla, systemd garantiza el reinicio sin intervención manual.
* **Network Isolation:** Cada worker se integra en una red aislada (`red.network`) definida de forma declarativa, evitando colisiones con otros servicios del host.
* **Persistence:** El estado de los servicios se mantiene activo tras reinicios del hardware mediante la persistencia del gestor de servicios de usuario (`loginctl enable-linger`).

## 7. Monitorización y Telemetría
Para auditoría técnica de los nodos en tiempo real, se utilizan las herramientas estándar de Linux:

* **Estado del Servicio:** `systemctl --user status worker.service`
* **Logs de Aplicación:** `journalctl --user -u worker.service -f --since "1 hour ago"`
* **Consumo de Recursos:** `podman stats`

## 8. Enlaces y Referencias
* **Dataset Source:** [TensorFlow Datasets - MNIST](https://www.tensorflow.org/datasets/catalog/mnist)
* **Documentación Quadlet:** [Podman Quadlet Guide](https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html)
* **Ansible Systemd Module:** [Community.General.Systemd](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/systemd_module.html)

---


>TODO: Optimizar el Dockerfile usando multi-stage build para reducir el tamaño de la imagen al máximo; así el archivo .tar será mucho más ligero y se transferirá más rápido a los workers.
