# Orchestration Trade-offs in Edge Computing: systemd vs Kubernetes

Edge environments challenge conventional cloud-native orchestration models due to limited resources and simplified deployment requirements. This work analyzes the trade-offs between Kubernetes and systemd as orchestration solutions for edge nodes. Using a set of representative workloads and fault-injection experiments, the study evaluates performance, resilience, and management complexity, offering design insights for selecting appropriate orchestration mechanisms in edge computing scenarios

---

# Entrega 1: Sistema parametrizable de N nodos con Ansible

![Podman](https://img.shields.io/badge/Podman-Rootless-892CA0?style=flat-square&logo=podman)
![Systemd](https://img.shields.io/badge/Systemd-Orchestration-darkgreen?style=flat-square&logo=linux)
![Entrega](https://img.shields.io/badge/Entrega-1-blue?style=flat-square)

## Objetivo

Crear un ansible que aixequi un Sistema amb N nodes (parametritzable) de systemd i que tot el tema de la comunicació i orquestració ja estigui fet.

---

## 1. Árbol de Directorios del Proyecto

    ansible-deploy/
    ├── inventory.ini             # Definición de los N nodos (IPs y roles)
    ├── group_vars/
    │   └── all.yml               # Variables globales (usuario, versión de imagen)
    ├── playbook.yml              # El orquestador principal
    ├── templates/                # Plantillas dinámicas (Jinja2)
    │   ├── edge.network.j2       # Red virtual Quadlet
    │   ├── web.container.j2      # Contenedores para los N nodos workers
    │   ├── balancer.container.j2 # Contenedor del balanceador
    │   └── nginx-lb.conf.j2      # Configuración dinámica del balanceo

---
## 2. Variables Globales (`group_vars/all.yml`)

## 3. Preparación del Inventario (`inventory.ini`)

## 4. Estructura de Archivos Quadlet (Templates Jinja2)
Para que el sistema sea dinámico, usaremos plantillas que Ansible rellenará automáticamente.

### Template de la Red: `templates/edge.network.j2`

### Template del Worker: `templates/web.container.j2`

### Template del Contenedor Balanceador: `templates/lb.container.j2`

### Template del Balanceador: `templates/nginx-lb.conf.j2`

---

## 5. El Playbook Maestro (`playbook.yml`)
Este script ejecuta la lógica en el orden correcto para garantizar la resiliencia y orquestación.

```yaml
---
- name: "Hito: Sistema Proactivo de N nodos"
  hosts: all
  tasks:
    - name: Habilitar linger para persistencia rootless
      become: yes
      command: "loginctl enable-linger {{ ansible_user }}"
      args:
        creates: "/var/lib/systemd/linger/{{ ansible_user }}"

    - name: Crear directorio de Quadlets
      file:
        path: "~/.config/containers/systemd"
        state: directory
        mode: '0755'

    - name: Desplegar Red Quadlet
      template:
        src: "templates/edge.network.j2"
        dest: "~/.config/containers/systemd/edge.network"

    - name: Crear carpeta para el volumen de la app
      file:
        path: "~/html_app"
        state: directory
      when: "'workers' in group_names"

    - name: Crear index.html personalizado para verificar balanceo
      copy:
        dest: "~/html_app/index.html"
        content: "<h1>Hola! Estas siendo atendido por el worker: {{ inventory_hostname }}</h1>\n"
      when: "'workers' in group_names"

    - name: Desplegar Quadlet del Worker
      template:
        src: templates/web.container.j2
        dest: "~/.config/containers/systemd/web.container"
      when: "'workers' in group_names"

    - name: Arrancar servicio Worker
      systemd:
        scope: user
        daemon_reload: yes
        name: web.service
        state: started
      when: "'workers' in group_names"

    - name: Crear configuración de Nginx Balanceador
      template:
        src: templates/nginx-lb.conf.j2
        dest: "/tmp/nginx-lb.conf"
      when: "'balancer' in group_names"

    - name: Desplegar Quadlet del Balanceador
      template:
        src: templates/lb.container.j2
        dest: "~/.config/containers/systemd/balancer.container"
      when: "'balancer' in group_names"

    - name: Arrancar servicio Balanceador
      systemd:
        scope: user
        daemon_reload: yes
        name: balancer.service
        state: started
      when: "'balancer' in group_names"
```
---

## 6. Pasos para la ejecución y validación


### FASE 0: Instalación

Asegúrate de tener Ansible instalado en tu máquina anfitriona o en una VM de gestión.

```bash
# Actualizar el sistema y preparar repositorios
sudo apt update
sudo apt install software-properties-common

#Añadir el repositorio oficial de Ansible
sudo add-apt-repository --yes --update ppa:ansible/ansible

#Instalar Ansible
sudo apt install ansible -y
```


### Fase 1: Forjar la "Llave Maestra" en tu WSL

Lo primero es crear una nueva identidad (llave SSH) exclusiva para tu máquina de control.

1. **Genera la llave:**
   Ejecuta el siguiente comando en tu terminal de Ubuntu:
   ```bash
   ssh-keygen -t rsa -b 4096
   ```
2. **Acepta todo por defecto:**
   El sistema te hará tres preguntas (dónde guardarla y si quieres ponerle contraseña). **Pulsa `Enter` tres veces seguidas** sin escribir nada. Esto creará una llave sin contraseña, indispensable para que Ansible pueda automatizar sin pedirte que teclees nada.

---

### Fase 2: Repartir las "Cerraduras" a los Nodos Edge

Ahora vamos a enviar la llave pública (la cerradura) a tus máquinas virtuales. Durante este paso, te pedirá la contraseña del usuario `littledragon` por última vez.

1. **Instala la llave en el Nodo A (192.168.1.101):**
   ```bash
   ssh-copy-id littledragon@192.168.1.101
   ```
   *(Si te pregunta `Are you sure you want to continue connecting?`, escribe `yes` y pulsa Enter. Luego, mete la contraseña de littledragon).*

2. **Instala la llave en el Nodo B (192.168.1.102):**
   ```bash
   ssh-copy-id littledragon@192.168.1.102
   ```

3. **Prueba de fuego (Verificación):**
   Intenta entrar al Nodo B desde tu WSL:
   ```bash
   ssh littledragon@192.168.1.102
   ```
   Si entras directamente sin que te pida contraseña, ¡lo has conseguido! Escribe `exit` para volver a tu WSL.

---

### Fase 3: Preparar el Proyecto en WSL (Aviso Crítico de Windows)

Aquí hay una trampa muy común al usar WSL con Ansible: **Los permisos de archivos.**
Si tienes tus archivos de Ansible guardados en tu escritorio de Windows (por ejemplo en `/mnt/c/Users/TuUsuario/Desktop/...`), Ansible **va a fallar** por razones de seguridad, ya que considera que el sistema de archivos de Windows es "inseguro" para guardar llaves e inventarios.

Tus archivos deben vivir en el sistema de archivos de Linux (la "casita" `~`).

1. **Crea una carpeta en tu WSL para el proyecto:**
   ```bash
   mkdir ~/tfg-ansible
   cd ~/tfg-ansible
   ```
2. **Recrea aquí tus archivos y carpetas:**
   Si no los tienes aquí, crea la estructura rápidamente usando `nano`. Debes tener exactamente esto dentro de `~/tfg-ansible`:
   * `inventory.ini`
   * `playbook.yml`
   * `group_vars/all.yml`
   * `templates/edge.network.j2`
   * `templates/web.container.j2`
   * `templates/nginx-lb.conf.j2`
   * `templates/lb.container.j2`

*(Puedes usar `nano inventory.ini`, pegar el texto, hacer `Ctrl+O`, `Enter`, `Ctrl+X`. Repite con todos los archivos que repasamos en el mensaje anterior).*

---

### Fase 4: El Momento de la Verdad

Ya tienes a tu Director de Orquesta con acceso VIP a los nodos y tu partitura (los archivos YAML y plantillas) en el lugar seguro de Linux.

Asegúrate de estar en la carpeta correcta:
```bash
cd ~/tfg-ansible
```

Y lanza el misil de la automatización:
```bash
ansible-playbook -i inventory.ini playbook.yml
```

Verás cómo Ansible se conecta, crea las redes, levanta los workers, configura el Nginx temporal, lanza el balanceador y deja todo listo en cuestión de segundos. Cuando termine, abre tu navegador en Windows y entra a `http://192.168.1.101` para ver tu clúster balanceando el tráfico.

**Prueba de Resiliencia**: Apaga el **Nodo B** (`sudo reboot`). Vuelve a hacer `curl` al balanceador. El sistema debe seguir respondiendo a través del **Nodo A** sin intervención manual.

---

## Checklist de éxito para tu entrega:
* [ ] ¿El sistema escala a 3 nodos solo tocando el `inventory.ini`? **(Parametrizable)**.
* [ ] ¿El contenedor arranca solo tras un `sudo reboot`? **(Resiliencia systemd)**.
* [ ] ¿El tráfico se reparte entre nodos? **(Balanceada)**.
* [ ] ¿Todo el despliegue se hace desde una sola máquina? **(Orquestada vía Ansible)**.

Este Hands-on cierra la **Fase 1** de tu TFG y te deja listo para empezar la **Fase 2: Motor Proactivo** (Semana 6).