# Orquestación Ansible: Clúster Edge Multi-Protocolo (Kubernetes/K3s)

Este directorio contiene la Infraestructura como Código (IaC) basada en Ansible para el aprovisionamiento automatizado y la gestión del ciclo de vida de nodos en un clúster ligero de Kubernetes (K3s), diseñado específicamente para entornos de procesamiento perimetral (*Edge Computing*).

## Arquitectura e Implementación Técnica

El sistema evoluciona desde la orquestación nativa (Systemd/Podman) hacia un modelo declarativo y centralizado utilizando K3s, una distribución de Kubernetes optimizada para el Edge (IoT/ARM):

* **Motor de Contenedores (`containerd`):** Se sustituye Podman por el motor interno nativo de Kubernetes. La gestión de imágenes y procesos queda bajo el control absoluto del componente Kubelet del nodo.
* **Manifiestos Declarativos (YAML):** Se elimina el uso de Quadlets de Systemd. En su lugar, el estado deseado se define en el directorio `k8s-manifests/` (ej. `worker-app.yaml`), inyectando variables dinámicamente y aplicando la configuración al clúster mediante `kubectl apply`.
* **Red Definida por Software (SDN):** El aislamiento y la conectividad no dependen de redes locales de host, sino de la red virtual del clúster (CNI, *Container Network Interface* como Flannel), permitiendo la comunicación transparente entre nodos.
* **Resiliencia y Auto-Recuperación:** El bucle de reconciliación (*Reconciliation Loop*) de Kubernetes garantiza que el estado real del clúster coincida siempre con el estado declarado, levantando nuevos Pods automáticamente ante cualquier fallo o caída del Worker.

## Diseño Modular y Despliegue Dinámico (Air-Gapped)

El pipeline de despliegue es completamente **independiente al protocolo de comunicación** (HTTP/REST, gRPC, ZeroMQ).

La inyección del entorno se controla dinámicamente en tiempo de ejecución. En lugar de editar ficheros estáticos, la ruta del experimento se sobrescribe al vuelo utilizando variables extra (`-e "experimento_path=..."`), permitiendo pivotar los protocolos de IA sin alterar el código fuente.

Para optimizar los recursos del hardware perimetral y asegurar la resiliencia en redes sin acceso a internet, la arquitectura mantiene un patrón **Air-Gapped** adaptado a K3s:

1. Ansible itera sobre el protocolo seleccionado y compila la imagen OCI de forma centralizada en el nodo de control.
2. La imagen se empaqueta en un artefacto inmutable (`.tar`) y se transfiere vía SSH a los Workers.
3. Se inyecta directamente en el *namespace* interno de K3s utilizando `k3s ctr images import`, liberando a los dispositivos Edge de la pesada carga computacional de compilación y descarga externa.

## Seguridad y Zero-Touch Provisioning

Para lograr una automatización absoluta sin intervención humana (Zero-Touch) y sin comprometer la seguridad del repositorio, la escalada de privilegios se gestiona mediante el directorio `group_vars/`.

El acceso de administrador (`sudo`) requerido para tareas de bajo nivel (como interactuar con `k3s` o reiniciar el sistema) se inyecta desde `group_vars/workers.yml` (archivo excluido explícitamente vía `.gitignore`), **eliminando la necesidad de introducir contraseñas interactivas (`-K`)** durante el despliegue.

## Requisitos e Inventario

La topología completa del clúster se encuentra unificada en el archivo `inventory.ini`. El nodo de control orquestador (Master) se comunica a través de la API de Kubernetes (`kubectl`) y también requiere acceso SSH sin contraseña hacia los entornos perimetrales para la inyección de imágenes y extracción de métricas globales.

### Configuración del Inventario (`inventory.ini`)

El inventario está estructurado segregando el entorno de control local del plano de ejecución en el Edge:

```ini
[master]
localhost ansible_connection=local

[workers]
node-a ansible_host=192.168.98.143
node-b ansible_host=192.168.98.144
```

### Parámetros de Red y Puertos

Por defecto, la infraestructura expone un puerto unificado a través de un `Service` de tipo `NodePort` o interconectividad de Pods:

* **Puerto de Servicio:** `8000` (declarado mediante la variable global `web_port` en `group_vars/all.yml`).
* Los servicios quedan vinculados dentro del ecosistema K3s, permitiendo al nodo Master la inyección de cargas de trabajo directamente hacia las IPs del clúster.

## Documentación de Ejecución y Benchmarking

El directorio incluye herramientas para gestionar la infraestructura y realizar pruebas de estrés de rigor científico, evaluando el "Impuesto Arquitectónico" (*Architectural Overhead*) de Kubernetes frente a arquitecturas nativas.

### 1. Documentación de Playbooks

#### Playbook de Despliegue (`playbook.yml`)

Ejecuta el aprovisionamiento de un protocolo específico (requiere inyectar `-e "experimento_path=..."`).

1. **Construcción y Distribución (Air-Gapped):** Compila la imagen OCI en el nodo Master, la transfiere por SSH y la inyecta en el motor `containerd` de cada nodo usando `k3s ctr`.
2. **Despliegue Declarativo:** Inyecta los manifiestos YAML desde `k8s-manifests/` hacia el clúster a través de `kubectl apply`.
3. **Validación:** Kubelet asume el control e inicializa los contenedores (Pods) hasta alcanzar el estado `Ready`.

#### Playbook de Destrucción (`clean.yml`)

Ejecuta una purga de infraestructura agresiva, vital para evitar **contaminación de métricas** (caché en RAM y procesos zombie) antes de pivotar entre arquitecturas:

1. **Purga Lógica:** Elimina los recursos del clúster descritos en los manifiestos.
2. **Purga de Motor:** Limpia las imágenes del registro interno usando `k3s crictl rmi`.
3. **Hard Reboot (Opcional en transición):** Preparación del sistema operativo limpio para evitar el estrangulamiento térmico (*Thermal Throttling*) de la CPU en posteriores ejecuciones de benchmark.

### 2. El Pipeline de Evaluación: `generate_benchmarks.sh`

Script Bash avanzado que automatiza el proceso de pruebas para los diferentes protocolos bajo Kubernetes.

1. **Despliegue Limpio:** Ejecuta `clean.yml` y despliega el nuevo protocolo dinámicamente.
2. **Medición Base (Resolución de Nodo):** Mapea dinámicamente el nombre lógico del nodo en K3s a su IP física y ejecuta `free -m` vía SSH. Esto evita las latencias del *Metrics Server* de Kubernetes y garantiza la captura del consumo **Global** (OS + K3s Overhead).
3. **Ingeniería del Caos (Chaos Testing):** Fuerza la eliminación abrupta de un Pod (`kubectl delete pod --force`).
4. **MTTR:** Mide matemáticamente en milisegundos el Tiempo Medio de Recuperación (*Mean Time To Recovery*) monitorizando el bucle de reconciliación hasta que el nuevo Pod pasa a estado `Ready`.
5. **Prueba de Carga:** Ejecuta la simulación de inferencia MNIST en red y extrae los datos mediante Regex, consolidando un *Data Lake* unificado en formato CSV.

---

## Instrucciones de Uso

### Opción A: Despliegue Manual por Protocolo

Útil para depuración y pruebas aisladas:

```bash
# 1. Limpieza de la infraestructura actual del clúster
ansible-playbook -i inventory.ini clean.yml

# 2. Despliegue inyectando la variable del protocolo
ansible-playbook -i inventory.ini playbook.yml -e "experimento_path=../2-src-protocols/01-http-json"
ansible-playbook -i inventory.ini playbook.yml -e "experimento_path=../2-src-protocols/02-grpc-protobuf"
ansible-playbook -i inventory.ini playbook.yml -e "experimento_path=../2-src-protocols/03-zeromq-protobuf"
ansible-playbook -i inventory.ini playbook.yml -e "experimento_path=../2-src-protocols/04-zeromq-messagepack"
```

### Opción B: Ejecución Global Automatizada (Zero-Touch)

El método formal diseñado para extraer las métricas comparativas del TFG:

```bash
# 1. Configurar la clave de administrador local (solo la primera vez)
echo 'ansible_become_pass: "TU_CONTRASEÑA_AQUI"' > group_vars/workers.yml

# 2. Dar permisos de ejecución al script de benchmarking
chmod +x generate_benchmarks.sh

# 3. Lanzar la evaluación global
./generate_benchmarks.sh

```

*(Los resultados consolidados se guardarán automáticamente en `3-benchmarks-results/resultados_globales.csv` listos para su análisis estadístico).*