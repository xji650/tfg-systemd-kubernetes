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

### Paso 1: Configuración de Claves SSH
Se requiere intercambio de claves RSA para permitir la ejecución desatendida de Ansible:
```bash
ssh-keygen -t rsa -b 4096
ssh-copy-id -i ~/.ssh/id_rsa.pub user@<ip-nodo>
```

### Paso 2: Aprovisionamiento (Ansible)
El despliegue automatiza la habilitación de **Linger**, la creación de la red virtual Quadlet y el build local de la imagen de aplicación. 

#### Opción A: Despliegue Estándar
Para levantar el clúster de forma normal sin extraer métricas de infraestructura:
```bash
ansible-playbook -i inventory.ini playbook.yml -K
```

#### Opción B: Despliegue con Benchmark (Extracción de Métricas)
Para extraer los datos del Plano de Gestión ($T_{deploy}$, Consumo en Reposo, $T_{recovery}$), se ejecutará el script de automatización. Este script envuelve la ejecución de Ansible y aplica pruebas de Chaos Engineering sobre los nodos perimetrales:
```bash
chmod +x benchmark_infra.sh
./benchmark_infra.sh
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
## 9. Demo

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


//TODO: Optimizar el Dockerfile usando multi-stage build para reducir el tamaño de la imagen al máximo; así el archivo .tar será mucho más ligero y se transferirá más rápido a los workers.

1. El falso 1% de CPU (Desajuste de variables en el JSON)
El problema: Al principio, la tabla mostraba un CPU Promedio de apenas un 1.05%, lo cual era imposible para un proceso tan pesado como parsear JSON masivos.

La causa: Había un desajuste entre las llaves del diccionario JSON. El Worker devolvía el dato con un nombre (ej. cpu_usage), pero el Maestro intentaba leerlo con otro (ej. cpu_promedio). Al no encontrarlo, Python asignaba un 0, hundiendo la media global.

La solución: Sincronizamos los nombres exactos de las variables (ram_mb, cpu_percent, t_proc_ms) entre el return del Worker y el cálculo del Maestro.

2. Mediciones de CPU a cero (El comportamiento de psutil)
El problema: Incluso con los nombres correctos, el Worker a veces devolvía 0.0% de uso de CPU.

La causa: La función psutil.cpu_percent(interval=None) necesita comparar el tiempo de CPU entre dos momentos. Si la llamábamos solo una vez o sin inicializarla, no tenía un punto de referencia y daba 0.

La solución: Añadimos una "llamada fantasma" a process.cpu_percent(interval=None) justo al inicio del endpoint /procesar para limpiar el buffer, y una segunda llamada al final para capturar el porcentaje exacto (el delta) que había consumido esa petición HTTP en concreto. Gracias a esto, vimos el 99.2% real.

3. El tiempo total astronómico y Throughput a cero (Choque de relojes)
El problema: En uno de los tests, el Tiempo Total dio 1.780.594.085 segundos (1.78 billones) y el Throughput se quedó en 0.00 img/s.

La causa: Estábamos mezclando dos tipos de relojes en Python. Para el inicio usamos time.perf_counter() (un reloj relativo de alta precisión) y para el final usamos time.time() (el reloj absoluto del sistema Unix). Al restarlos, dio un número absurdo.

La solución: Unificamos todo el script del Maestro para que utilizara exclusivamente time.perf_counter() tanto para inicio_t como para fin_t, logrando una precisión de milisegundos perfecta.
