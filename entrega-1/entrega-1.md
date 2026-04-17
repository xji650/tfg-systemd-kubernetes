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
    │   ├── red.network.j2       # Red virtual Quadlet
    │   ├── web.container.j2      # Contenedores para los N nodos workers
    │   ├── lb.container.j2 # Contenedor del balanceador
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

## 5. Playbook Maestro (`playbook.yml`)
Este script ejecuta la lógica en el orden correcto para garantizar la resiliencia y orquestación.

```yaml
---
- name: "Hito: Sistema Proactivo de N nodos"
  hosts: all
  tasks:
    # ---------------------------------------------------------
    # 1. PERSISTENCIA Y PREPARACIÓN BASE
    # ---------------------------------------------------------
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
        src: "templates/red.network.j2"
        dest: "~/.config/containers/systemd/red.network"
    
    - name: Recargar systemd de usuario
      systemd:
        scope: user
        daemon_reload: yes

    - name: Arrancar red Quadlet
      systemd:
        scope: user
        name: red-network.service
        state: started
        enabled: yes

    # ---------------------------------------------------------
    # 2. DESPLIEGUE DE LOS WORKERS (Aplicación Web)
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # 3. DESPLIEGUE DEL BALANCEADOR DE CARGA
    # ---------------------------------------------------------
    - name: Crear configuración de Nginx Balanceador
      template:
        src: templates/nginx-lb.conf.j2
        dest: "~/nginx-lb.conf"
        mode: '0644'
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

## 7. Playbook de Limpieza (`clean.yml`)
```bash
ansible-playbook -i inventory.ini clean.yml -K
```

---

## Checklist de éxito para tu entrega:
* [ ] ¿El sistema escala a 3 nodos solo tocando el `inventory.ini`? **(Parametrizable)**.
* [ ] ¿El contenedor arranca solo tras un `sudo reboot`? **(Resiliencia systemd)**.
* [ ] ¿El tráfico se reparte entre nodos? **(Balanceada)**.
* [ ] ¿Todo el despliegue se hace desde una sola máquina? **(Orquestada vía Ansible)**.

Este Hands-on cierra la **Fase 1** de tu TFG y te deja listo para empezar la **Fase 2: Motor Proactivo** (Semana 6).