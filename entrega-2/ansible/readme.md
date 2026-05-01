# Pasos para la ejecución 

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
| **Balanceador** | Nginx | `8888` | TCP | Punto de entrada único para el clúster |
| **SSH** | OpenSSH Server | `22` | TCP | Gestión y despliegue con Ansible |


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
python3 master.py
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

---
## 10. Demo

### Paso 1: Mostrar que es "Declarativo" (El Blueprint)
Antes de ejecutar nada, demuestra que estás usando systemd como un orquestador real y no lanzando contenedores a mano.
* **En el Nodo A:**
  ```bash
  cat ~/.config/containers/systemd/worker.container
  ```
* **Qué decirle al tutor:** *"Como ves, no ejecuto comandos de Podman. Defino el estado deseado en este Quadlet, incluyendo la red virtual y las políticas de reinicio, y systemd se encarga de todo el ciclo de vida del contenedor en espacio de usuario (rootless)."*

### Paso 2: Ejecutar el Sistema Distribuido (El flujo feliz)
Aquí es donde demuestras el particionamiento del dataset.
* **En el Nodo A (Terminal derecha):** Deja los logs del trabajador monitorizándose en tiempo real.
  ```bash
  journalctl --user -u worker.service -f
  ```
* **En el WSL (Terminal izquierda):** Ejecuta tu orquestador de datos.
  ```bash
  python master.py
  ```
* **Qué decirle al tutor:** *"Al ejecutar el maestro, vemos cómo descarga las 60.000 imágenes, calcula matemáticamente la división entre los nodos activos y despacha los paquetes. Si miramos la terminal de la derecha, vemos en tiempo real cómo el contenedor del Nodo A recibe y cuenta exactamente sus 30.000 imágenes, devolviendo un HTTP 200 OK."*

### Paso 3: Demostrar la eficiencia energética (El argumento contra Kubernetes)
Tu informe habla de un consumo de ~215 MB. Esto es una ventaja brutal frente a Kubernetes (que consume gigabytes solo para existir). Hay que mostrarlo.
* **En el Nodo A:**
  ```bash
  podman stats --no-stream
  ```
  *(También puedes usar `systemd-cgtop` si lo prefieres).*
* **Qué decirle al tutor:** *"Este es uno de los trade-offs principales del estudio. Al delegar la orquestación a systemd en lugar de instalar un agente pesado de Kubernetes (como Kubelet), el contenedor procesa miles de imágenes consumiendo apenas 200 MB de RAM. Casi el 100% del hardware del Edge se dedica a la carga útil, no a la gestión."*

### Paso 4: La prueba del Caos (Demostrar la Resiliencia)
Tu informe dice: *"Verificación de la auto-recuperación... ante fallos"*. Los tutores aman ver las cosas romperse y arreglarse solas. Vamos a "asesinar" a tu worker.
* **En el Nodo A:**
  1. Primero, mira el estado del servicio:
     ```bash
     systemctl --user status worker.service
     ```
  2. Ahora, mata el contenedor a lo bruto (simulando un fallo crítico de software o de memoria):
     ```bash
     podman stop worker-mnist-node-a -t 0
     ```
  3. Rápidamente, vuelve a mirar el estado y los logs:
     ```bash
     systemctl --user status worker.service
     journalctl --user -u worker.service -n 10
     ```
* **Qué decirle al tutor:** *"Acabo de matar el contenedor forzosamente simulando un colapso en el Edge. Como la infraestructura es gestionada por systemd con la directiva `Restart=always`, el sistema ha detectado la caída y ha redesplegado el contenedor automáticamente en menos de 3 segundos, quedando listo para el siguiente paquete de datos sin que yo intervenga."*

---

```
ansible all -i inventory.ini -m shell -a "ip route add default via 192.168.0.1" -b -K
```