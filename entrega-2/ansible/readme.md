# Orquestación Ansible: Clúster Edge Multi-Protocolo

Este repositorio contiene la Infraestructura como Código (IaC) basada en Ansible para el aprovisionamiento automatizado y la gestión del ciclo de vida de los nodos Worker en un entorno de procesamiento perimetral.

## Arquitectura e Implementación Técnica

El sistema está diseñado bajo el paradigma de contenedores *rootless* para maximizar la seguridad perimetral, delegando el control de los servicios directamente a Systemd:

*   **Systemd Linger:** Se habilita la persistencia de procesos en segundo plano para el usuario del sistema (`littledragon`) ejecutando `loginctl enable-linger`. Esto garantiza que los servicios se mantengan activos tras cerrar la sesión SSH.
*   **Podman Quadlets:** Se elimina el uso tradicional de `docker-compose`. En su lugar, el estado deseado se declara mediante Quadlets, inyectando plantillas `Jinja2` directamente en `~/.config/containers/systemd/` para generar redes (`red.network`) y contenedores (`worker.container`) de forma nativa.
*   **Aislamiento y Alta Disponibilidad:** El sistema crea una red virtual dedicada (`red-interna`). Además, la unidad de Systemd aplica políticas de auto-recuperación (`Restart=always` con 3 segundos de espera) para garantizar la resiliencia del Worker ante fallos.

## Diseño Modular y Soporte Multi-Protocolo

El pipeline de despliegue ha sido refactorizado para ser completamente agnóstico al protocolo de comunicación (HTTP/REST, gRPC, ZeroMQ). 

La inyección del entorno y dependencias específicas se controla de forma dinámica mediante la variable `experimento_path` definida en las variables de grupo. Para pivotar la arquitectura del clúster entero, basta con modificar el puntero en el inventario:

```yaml
# Rutas disponibles para evaluación de rendimiento:
# experimento_path: "../results/http"
# experimento_path: "../results/grpc"
experimento_path: "../results/zeromq"
```

Durante el despliegue, Ansible iterará sobre esta ruta para transferir el `Dockerfile`, el código fuente (`worker.py`) y las interfaces (`mnist.proto` si procede) al directorio de *build* (`~/mnist-build`) de cada nodo perimetral.

## Requisitos e Inventario
La topología del clúster se define bajo el grupo `[workers]`. El nodo de control requiere acceso SSH sin contraseña a las IPs declaradas usando la clave RSA estándar (`~/.ssh/id_rsa`).

Nodos actualmente registrados:
*   `node-a` (IP: 192.168.98.143)
*   `node-b` (IP: 192.168.98.144)

Todos los Workers exponen el puerto unificado `8000` (definido en la variable `web_port`) al orquestador central.

## Documentación de Playbooks

### 1. Playbook de Despliegue (`playbook.yml`)
Ejecuta el aprovisionamiento integral (Hito: Sistema Proactivo de N nodos):
1.  **Preparación Base:** Activa el *linger* y despliega la red virtual a través de Quadlets, reiniciando el *daemon* de usuario.
2.  **Construcción Nativa:** Crea el directorio de trabajo, transfiere el código del experimento seleccionado y compila la imagen OCI (`localhost/worker-mnist:v1`) en el destino usando Podman.
3.  **Ejecución:** Despliega el Quadlet del contenedor y delega a Systemd el reinicio y habilitación del `worker.service`.

### 2. Playbook de Destrucción (`clean.yml`)
Ejecuta una purga de infraestructura agresiva, necesaria para garantizar un entorno limpio antes de cambiar de protocolo y evitar interferencias en las métricas:
1.  **Detención de Servicios:** Apaga de forma segura `worker.service` y `red-network.service` a nivel de usuario.
2.  **Purga de Ficheros:** Elimina los manifiestos `.container` y `.network`, además del código fuente almacenado en `~/mnist-build`.
3.  **Limpieza de Podman:** Fuerza el borrado de los contenedores vivos, la red interna virtual y las imágenes locales compiladas.
4.  **Reset de Systemd:** Limpia cualquier estado de unidad fallida residual en memoria (`reset-failed`).