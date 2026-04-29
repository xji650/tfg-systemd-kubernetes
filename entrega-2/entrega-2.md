# Orchestration Trade-offs in Edge Computing: systemd vs Kubernetes

Edge environments challenge conventional cloud-native orchestration models due to limited resources and simplified deployment requirements. This work analyzes the trade-offs between Kubernetes and systemd as orchestration solutions for edge nodes. Using a set of representative workloads and fault-injection experiments, the study evaluates performance, resilience, and management complexity, offering design insights for selecting appropriate orchestration mechanisms in edge computing scenarios

---

# Informe de Seguimiento: Entrega 2

![Podman](https://img.shields.io/badge/Podman-Rootless-892CA0?style=flat-square&logo=podman)
![Systemd](https://img.shields.io/badge/Systemd-Orchestration-darkgreen?style=flat-square&logo=linux)
![Entrega](https://img.shields.io/badge/Entrega-2-blue?style=flat-square)

---

## 1. Resumen Ejecutivo
Tras la consolidación de la infraestructura base del Systemd, esta segunda fase ha consistido en el despliegue de una carga de trabajo funcional sobre el clúster. Se ha implementado un sistema de **procesamiento distribuido** utilizando el dataset MNIST, migrando de un servicio estático (Nginx) a un servicio de computación activa (API Python). La orquestación se ha realizado íntegramente mediante **Ansible** y **Podman Quadlets**, validando la capacidad de systemd para gestionar servicios de cálculo intensivo.

## 2. Objetivos
1.  **Ingesta y Partición de Datos:** Desarrollo de un Nodo Maestro capaz de descargar, preprocesar y segmentar un dataset de visión artificial en $N$ partes proporcionales al número de nodos activos.
2.  **Computación Distribuida:** Implementación de Nodos Trabajadores (Fills) que ejecutan tareas de conteo de imágenes de forma aislada en contenedores rootless.
3.  **Consolidación de Quadlets:** Transición completa hacia el despliegue declarativo, eliminando el uso de comandos imperativos en los nodos.
4.  **Resiliencia Crítica:** Verificación de la auto-recuperación de servicios mediante las directivas de systemd ante fallos en la capa de aplicación.

## 3. Arquitectura del Sistema
El sistema opera bajo un modelo de arquitectura **Master-Worker** (Maestro-Trabajador) distribuido sobre una red L3.



### 3.1 Nodo Maestro (Control Plane)
Localizado en la máquina de gestión (WSL), el script `master.py` utiliza la librería `tensorflow-datasets` para obtener el dataset MNIST. La lógica de negocio calcula el tamaño de la partición mediante la fórmula:
$$tamano\_particion = \frac{total\_imagenes}{N\_nodos}$$
Para garantizar la transmisión por red, los tensores se transforman en listas nativas de Python, asegurando la compatibilidad con la serialización JSON.

### 3.2 Nodo Trabajador (Edge Worker)
Cada nodo ejecuta una imagen OCI (`worker-mnist:v1`) construida localmente. El servicio está expuesto a través del puerto **8000** y es gestionado por una unidad de servicio de usuario de systemd generada por un Quadlet.

## 4. Implementación Técnica y Orquestación

### 4.1 Despliegue con Ansible
El playbook de esta entrega ha sido modificado para realizar un ciclo de vida completo de CI/CD en el Edge:
* **Build-on-Edge:** Ansible sincroniza el código fuente (`worker.py`) y el `Dockerfile`. La imagen se construye en el propio nodo para evitar la dependencia de un registro de imágenes externo, optimizando el uso del ancho de banda.
* **Configuración Declarativa:** Se despliegan plantillas Jinja2 para los archivos `.container` y `.network`, permitiendo que cada nodo reciba una configuración personalizada basada en su `inventory_hostname`.

### 4.2 Gestión mediante systemd Quadlets
Se ha validado que systemd actúa como un orquestador de bajo nivel altamente eficiente. Las unidades generadas incluyen:
* **Control de Dependencias:** El servicio del trabajador (`worker.service`) tiene una dependencia estricta de la red interna (`red-network.service`), asegurando que el contenedor no inicie hasta que la interfaz virtual esté operativa.
* **Políticas de Reinicio:** Se ha configurado `Restart=always` con un intervalo de 3 segundos, lo que permite recuperar el nodo de cómputo en caso de excepciones no controladas en el código Python.

## 5. Resultados de la Evaluación

Se han realizado pruebas de estrés enviando el dataset completo (60.000 imágenes) repartido entre dos nodos. Los resultados obtenidos son:

| Métrica | Resultado Nodo A | Resultado Nodo B |
| :--- | :--- | :--- |
| **Imágenes Asignadas** | 30,000 | 30,000 |
| **Estado de Salida** | Exitoso (200 OK) | Exitoso (200 OK) |
| **Persistencia Linger** | Validada (Activa) | Validada (Activa) |
| **Consumo RAM (Peak)** | ~215 MB | ~212 MB |

## 6. Conclusiones
El Hito 2 demuestra que la combinación de **Ansible + systemd Quadlets** es una alternativa viable y ligera a Kubernetes para tareas de computación distribuida en el Edge. Se ha logrado un sistema parametrizable donde añadir capacidad de cómputo es tan sencillo como añadir una IP al inventario. La infraestructura es resiliente, rootless y declarativa.