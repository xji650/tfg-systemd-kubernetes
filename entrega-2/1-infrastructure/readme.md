# Orquestación Ansible: Clúster Edge Multi-Protocolo

Este directorio contiene la Infraestructura como Código (IaC) basada en Ansible para el aprovisionamiento automatizado y la gestión del ciclo de vida de nodos Master y Worker en un entorno de procesamiento perimetral (*Edge Computing*).

## Arquitectura e Implementación Técnica

El sistema está diseñado bajo el paradigma de contenedores *rootless* para maximizar la seguridad perimetral, delegando el control de los servicios directamente a Systemd:

* **Systemd Linger:** Se habilita la persistencia de procesos en segundo plano para el usuario del sistema (`littledragon`) ejecutando `loginctl enable-linger`. Esto garantiza que los servicios se mantengan activos tras cerrar la sesión SSH.
* **Podman Quadlets:** Se elimina el uso tradicional de `docker-compose`. En su lugar, el estado deseado se declara mediante Quadlets, inyectando plantillas `Jinja2` directamente en `~/.config/containers/systemd/` para generar redes (`red.network`) y contenedores (`worker.container`) de forma nativa.
* **Aislamiento y Alta Disponibilidad:** El sistema crea una red virtual dedicada (`red-interna`). Además, la unidad de Systemd aplica políticas de auto-recuperación (`Restart=always` con 3 segundos de espera) para garantizar la resiliencia del Worker ante fallos.

## Diseño Modular y Despliegue Dinámico (Air-Gapped)

El pipeline de despliegue es completamente **independiente al protocolo de comunicación** (HTTP/REST, gRPC, ZeroMQ).

En esta versión optimizada, la inyección del entorno se controla dinámicamente en tiempo de ejecución. En lugar de editar ficheros estáticos, la ruta del experimento se sobrescribe al vuelo utilizando variables extra (`-e "experimento_path=..."`), permitiendo pivotar la arquitectura entera sin alterar el código fuente.

Para optimizar los recursos del hardware perimetral y asegurar la resiliencia en redes sin acceso a internet, la arquitectura utiliza un patrón **Air-Gapped**:

1. Ansible itera sobre el protocolo seleccionado y compila la imagen OCI de forma centralizada en el nodo de control (Master).
2. La imagen se empaqueta en un artefacto inmutable (`.tar`) y se transfiere vía SSH a los Workers.
3. Se carga directamente en el motor local (`podman load`), liberando a los dispositivos Edge de la pesada carga computacional de compilación y descarga de dependencias.

## Seguridad y Zero-Touch Provisioning

Para lograr una automatización absoluta sin intervención humana (Zero-Touch) y sin comprometer la seguridad del repositorio en el control de versiones, la escalada de privilegios se gestiona mediante un archivo de secretos local.

El acceso de administrador (`sudo`) requerido para tareas de bajo nivel (como activar el *Linger*) se inyecta desde `group_vars/workers.yml` (archivo excluido explícitamente vía `.gitignore`), **eliminando la necesidad de introducir contraseñas interactivas (`-K`)** durante el despliegue.

## Requisitos e Inventario

La topología completa del clúster y los roles de enrutamiento se encuentran unificados en el archivo `inventory.ini`. El nodo de control orquestador requiere acceso SSH sin contraseña hacia los entornos perimetrales mediante el intercambio previo de claves públicas RSA (`~/.ssh/id_rsa`).

### Configuración del Inventario (`inventory.ini`)

El inventario está estructurado segregando el entorno de control local del plano de ejecución en el Edge:

```ini
[master]
localhost ansible_connection=local

[workers]
node-a ansible_host=192.168.98.143
node-b ansible_host=192.168.98.144

```

* **Grupo `[master]`:** Define el nodo de control central (orquestador). Utiliza la directiva `ansible_connection=local` para optimizar las tareas de compilación interna, empaquetado y aprovisionamiento local (como la descarga del dataset MNIST) sin necesidad de saltos de red SSH artificiales hacia el propio host.
* **Grupo `[workers]`:** Registra los nodos perimetrales del clúster dedicados al cómputo pasivo. Cada host mapea su alias simbólico (`node-a`, `node-b`) a su dirección IPv4 correspondiente a través del parámetro nativo `ansible_host`.

### Parámetros de Red y Puertos

Por defecto, la infraestructura expone un puerto unificado en los contenedores para canalizar el tráfico hacia el microframework correspondiente:

* **Puerto de Servicio:** `8000` (declarado mediante la variable global `web_port` en los playbooks).
* Todos los servicios desplegados quedan vinculados de forma *rootless* a las interfaces físicas de los Workers, permitiendo al nodo Master la inyección paralela de cargas de trabajo directamente a través de los sockets expuestos de cada IP.


## Documentación de Ejecución y Benchmarking

El directorio incluye herramientas para gestionar la infraestructura de forma individual o mediante un pipeline de evaluación global.

### 1. Documentación de Playbooks

#### Playbook de Despliegue (`playbook.yml`)

Ejecuta el aprovisionamiento de un protocolo específico (requiere inyectar `-e "experimento_path=..."`).

1. **Preparación Base:** Activa el *linger* y despliega la red virtual a través de Quadlets, reiniciando el *daemon* de usuario.
2. **Construcción Centralizada y Distribución (Air-Gapped):** Compila la imagen OCI en el nodo orquestador basándose en el experimento seleccionado, la empaqueta en formato `.tar`, la transfiere a los nodos perimetrales vía SSH y la inyecta directamente en Podman (`podman load`).
3. **Ejecución:** Despliega el Quadlet del contenedor y delega a Systemd el reinicio y habilitación del `worker.service`.

#### Playbook de Destrucción (`clean.yml`)

Ejecuta una purga de infraestructura agresiva, necesaria para garantizar un entorno limpio antes de cambiar de protocolo y evitar interferencias en las métricas:

1. **Detención de Servicios:** Apaga de forma segura `worker.service` y `red-network.service` a nivel de usuario.
2. **Purga de Ficheros:** Elimina los manifiestos `.container` y `.network`, además del artefacto empaquetado `~/worker-mnist.tar`.
3. **Limpieza de Podman:** Fuerza el borrado de los contenedores vivos, la red interna virtual y las imágenes locales cargadas.
4. **Reset de Systemd:** Limpia cualquier estado de unidad fallida residual en memoria (`reset-failed`).

### 2. El Pipeline de Evaluación: `generate_benchmarks.sh`

Script Bash avanzado que automatiza proceso de pruebas para diferentes protocolos de comunicación. Realiza un ciclo continuo sobre los 3 protocolos (4 formas) implementados:

1. **Despliegue Limpio:** Ejecuta `clean.yml` y despliega el nuevo protocolo dinámicamente.
2. **Medición Base:** Captura el $T_{deploy}$ global y el consumo de RAM/CPU en reposo.
3. **Ingeniería del Caos (Chaos Testing):** Fuerza la caída abrupta de los contenedores (`podman kill`) en el clúster Edge.
4. **MTTR:** Mide matemáticamente el Tiempo Medio de Recuperación (*Mean Time To Recovery*) impulsado por Systemd.
5. **Prueba de Carga:** Ejecuta la simulación de inferencia MNIST en red y guarda los *logs* en la carpeta de resultados estructurada.

---

### Instrucciones de Uso

#### Opción A: Despliegue Manual por Protocolo

Útil para depuración y pruebas aisladas:

```bash
# 1. Limpieza de la infraestructura actual
ansible-playbook -i inventory.ini clean.yml


# 2. Despliegue 
## desplegar protocolo (http-json por defecto)
ansible-playbook -i inventory.ini playbook.yml

## desplegar un protocolo inyectando la variable
ansible-playbook -i inventory.ini playbook.yml -e "experimento_path=../2-src-protocols/01-http-json"
ansible-playbook -i inventory.ini playbook.yml -e "experimento_path=../2-src-protocols/02-grpc-protobuf"
ansible-playbook -i inventory.ini playbook.yml -e "experimento_path=../2-src-protocols/03-zeromq-protobuf"
ansible-playbook -i inventory.ini playbook.yml -e "experimento_path=../2-src-protocols/04-zeromq-messagepack"

```

#### Opción B: Ejecución Global Automatizada (Zero-Touch)

El método recomendado para extraer las métricas formales del TFG:

```bash
# 1. Configurar la clave de administrador local (solo la primera vez)
echo 'ansible_become_pass: "TU_CONTRASEÑA_AQUI"' > group_vars/workers.yml

# 2. Dar permisos de ejecución al pipeline
chmod +x generate_benchmarks.sh

# 3. Lanzar la evaluación global
./generate_benchmarks.sh

```

*(Los resultados de cada arquitectura se guardarán automáticamente en la carpeta `3-benchmarks-results/raw_logs/` del proyecto).*