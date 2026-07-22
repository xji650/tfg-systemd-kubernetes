# Guía Práctica de Despliegue y Demostración: Kubernetes (K3s)

El objetivo de este documento es detallar el procedimiento de despliegue automatizado del clúster MLOps en el Edge utilizando **K3s (Kubernetes ligero)**, así como proporcionar el guion de demostración técnica (Demo) para validar la orquestación, el particionamiento de datos y la resiliencia del sistema.

La tarea principal consiste en:

1. Desplegar un clúster Kubernetes mediante un patrón *Air-Gapped* usando Ansible.
2. Entrenar un modelo fundacional IA (PyTorch) en el nodo Master.
3. Distribuir el dataset MNIST en N partes hacia los Pods de inferencia (Workers) evaluando diferentes protocolos de red.
4. Retornar las métricas y predicciones al Master de forma directa.

---

## 1. Especificaciones de Infraestructura

* **Plano de Automatización:** Ansible 2.10+
* **Plano de Control (Orquestador):** Kubernetes API (K3s Server)
* **Gestor de Contenedores:** containerd (K3s Agent)
* **Red Virtual:** Flannel CNI
* **Dataset:** TensorFlow Datasets (MNIST - 60,000 imágenes)

## 2. Matriz de Conectividad y Puertos

El sistema requiere la apertura de los siguientes puertos para garantizar la orquestación y el flujo de datos:

| Componente | Puerto | Protocolo | Descripción |
| --- | --- | --- | --- |
| **SSH** | `22` | TCP | Aprovisionamiento con Ansible (Host) |
| **K3s API** | `6443` | TCP | Plano de control de Kubernetes (Master) |
| **Kubelet** | `10250` | TCP | Métricas y logs de los nodos (Workers) |
| **NodePort** | `30000` | TCP | Balanceador de carga para ingesta de datos IA |

---

## 3. Procedimiento de Aprovisionamiento (Ansible)

### Paso 1: Configuración de Claves SSH

Intercambio de claves para permitir la ejecución desatendida:

```bash
ssh-keygen -t rsa -b 4096
ssh-copy-id -i ~/.ssh/id_rsa.pub user@<ip-nodo>
```

### Paso 2: Despliegue Air-Gapped y Orquestación

El playbook automatiza la copia de la imagen `.tar`, la carga en el motor `containerd` y la aplicación de los manifiestos YAML contra la API del clúster.

Para desplegar un protocolo de comunicación específico inyectando la variable:

```bash
ansible-playbook -i inventory.ini playbook-k8s.yml -e "experimento_path=../2-src-protocols/01-http-json"
ansible-playbook -i inventory.ini playbook-k8s.yml -e "experimento_path=../2-src-protocols/02-grpc-protobuf"
ansible-playbook -i inventory.ini playbook-k8s.yml -e "experimento_path=../2-src-protocols/03-zeromq-protobuf"
ansible-playbook -i inventory.ini playbook-k8s.yml -e "experimento_path=../2-src-protocols/04-zeromq-messagepack"
```

### Paso 3: Ejecución del Reparto de Carga (MLOps)

Desde la máquina Master, se inicia el entrenamiento y el envío de datos a través del `Service NodePort`:

```bash
python3 master.py
```

## 4. Arquitectura de Resiliencia (Kubernetes)

La robustez del sistema ahora está gestionada globalmente por el plano de control:

* **Reconciliation Loop:** El estado deseado se define mediante un `Deployment`. Si un Pod falla o es eliminado, el *ReplicaSet* solicita inmediatamente al *Scheduler* la creación de uno nuevo.
* **Network Abstraction:** Los pods se comunican a través de un `Service` abstracto, haciendo que el script Master sea agnóstico a las caídas o cambios de IP de los contenedores físicos.
---

## 5. Guion de Demostración Técnica (Defensa del TFG)

Este apartado detalla los pasos para demostrar en directo al tribunal las capacidades arquitectónicas del sistema.

### Paso 1: Mostrar el Paradigma Declarativo (El Blueprint)

Antes de ejecutar la inferencia, demuestra cómo se orquesta la aplicación.

* **En el Nodo Master:**
```bash
cat worker-deployment.yaml
```


* **Qué decirle al tribunal:** *"A diferencia de la gestión imperativa inicial, aquí no ejecutamos contenedores directamente. Hemos declarado el estado deseado en este manifiesto (X réplicas, imagen, puertos). Ansible simplemente inyectó este manifiesto, y es la API de Kubernetes la que ha asumido el control de desplegarlos."*

### Paso 2: Ejecutar el Sistema Distribuido (Flujo MLOps)

Demuestra el balanceo de carga y el procesamiento de la IA.

* **En el Master (Terminal 1 - Logs):**
```bash
kubectl logs -l app=worker-mnist -f
```


* **En el Master (Terminal 2 - Ejecución):**
```bash
python master.py
```


* **Qué decirle al tribunal:** *"Al lanzar el script Master, la red neuronal fundacional se empaqueta junto con el dataset. El tráfico no va a las IPs físicas, sino al 'Service NodePort' de Kubernetes. En los logs (Terminal 1) podemos observar cómo el clúster balancea la carga de inferencia dinámicamente entre los diferentes Pods perimetrales."*

### Paso 3: Evidenciar el "Impuesto Arquitectónico" (El Trade-off)

Demuestra empíricamente el coste de usar Kubernetes frente a Systemd.

* **En el Master:**
```bash
kubectl top nodes
```


*(O ejecuta `free -m` en un Worker)*
* **Qué decirle al tribunal:** *"Este es el núcleo de la investigación. Mientras que Systemd gestionaba esta misma tarea consumiendo apenas 200 MB, aquí podemos ver que los nodos presentan una huella de memoria superior a los 850 MB. Este 'impuesto arquitectónico' es el coste de mantener el plano de control y la red virtual (Flannel) de Kubernetes activos en el Edge. Por esto mismo, el uso de serialización binaria ultraligera (MessagePack) fue vital para evitar el colapso del nodo."*

### Paso 4: Pruebas de Caos / Chaos Engineering (La Resiliencia)

Demuestra la principal ventaja de Kubernetes: la auto-recuperación global.

* **En el Master (Terminal 1 - Monitorización continua):**
```bash
kubectl get pods -w
```

* **En el Master (Terminal 2 - Inyección del fallo):** Simulamos una caída crítica borrando un pod a la fuerza.
```bash
kubectl delete pod <nombre-del-pod>
```

* **Qué decirle al tribunal:** *"Si simulamos un fallo fatal destruyendo un proceso, observamos en el monitor que Kubernetes no requiere intervención de Ansible. El bucle de reconciliación detecta la anomalía en el estado declarado y levanta una nueva réplica instantáneamente para garantizar la alta disponibilidad del servicio."*