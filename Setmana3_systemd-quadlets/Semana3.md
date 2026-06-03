## FASE 1: Fundamentos y comparativa

# Semana 3.1: Despliegue Declarativo con Podman Quadlets

![Podman](https://img.shields.io/badge/Podman-Rootless-892CA0?style=flat-square&logo=podman)
![Systemd](https://img.shields.io/badge/Systemd-Orchestration-darkgreen?style=flat-square&logo=linux)
![Semana](https://img.shields.io/badge/Semana-3.1-blue?style=flat-square)

## Objetivo

El objetivo de esta semana  es abandonar la generación imperativa de servicios (`podman generate systemd`) y transicionar a **Podman Quadlets**, la alternativa moderna oficial. Los Quadlets permiten definir contenedores, redes y volúmenes de forma declarativa (como si fueran YAMLs de Kubernetes), lo cual es el paso fundamental para poder parametrizar y automatizar el despliegue de los $N$ nodos con **Ansible** de forma limpia.

-----

## PARTE 0: Requisito Previo (Persistencia Linger)

Al igual que en la Semana 2, al ejecutar contenedores rootless (sin sudo), systemd necesita mantener los procesos vivos aunque cierres la sesión SSH.

```bash
# Activar la persistencia (si no lo hiciste previamente)
loginctl enable-linger $USER

# Verificar el estado
loginctl show-user $USER --property=Linger
```

-----

## PARTE 1: Conceptos Quadlet

**[Dónde ejecutar]:** En **Nodo A** (Exploración práctica).

**Explicación a fondo:**

  * **Adiós al `podman run` previo:** Ya no necesitas arrancar un contenedor a mano y luego decirle a systemd que lo copie.
  * **Archivos `.container`:** Escribimos un archivo de configuración plano. Cuando recargamos systemd, un generador interno de Podman lee ese archivo y crea el `.service` al vuelo en la memoria de Linux.
  * **Ruta estricta:** Para contenedores de usuario, los Quadlets **siempre** deben guardarse en `~/.config/containers/systemd/`. (Ojo: la ruta es diferente a la de la semana pasada, que era `~/.config/systemd/user/`).

<!-- end list -->

```bash
# Crear el directorio base para los Quadlets
mkdir -p ~/.config/containers/systemd/
```

-----

## PARTE 2: Despliegue Básico con Quadlets (Nginx)

Vamos a desplegar el mismo Nginx de la Semana 1 y 2, pero al estilo moderno.

### Paso 1: Crear el archivo `.container`

```bash
vim ~/.config/containers/systemd/web.container
```

Añade el siguiente contenido:

```ini
[Unit]
Description=Servidor Nginx Web con Quadlet
After=network-online.target

[Container]
Image=docker.io/library/nginx
PublishPort=8080:80
ContainerName=web-quadlet

[Service]
Restart=on-failure

[Install]
WantedBy=default.target
```

### Paso 2: Arrancar el servicio

Fíjate que no ejecutamos ningún comando de Podman. Solo hablamos con systemd.

```bash
# Le decimos a systemd que busque nuevos Quadlets y genere los .service
systemctl --user daemon-reload

# Arrancamos el servicio generado (con persistencia)
systemctl --user start web.service

# Verificamos
podman ps
systemctl --user status web.service
```

- En **Quadlets** `start` ya incorpora persistencia, por lo tanto ya no se usa `systemctl --user enable --now web.service`

-----

## PARTE 3: Proyecto Stack (Web + DB en Red Aislada)

Para tu hito de orquestación, necesitarás levantar entornos completos. Quadlet también maneja redes (`.network`) y volúmenes (`.volume`).

### Paso 1: Definir la Red

```bash
nano ~/.config/containers/systemd/mired.network
```

Contenido:

```ini
[Network]
NetworkName=red-edge
```

### Paso 2: Definir la Base de Datos (MariaDB)

```bash
nano ~/.config/containers/systemd/db.container
```

Contenido:

```ini
[Unit]
Description=MariaDB Database

[Container]
Image=docker.io/library/mariadb:10.11
ContainerName=db
Network=mired.network
Environment=MARIADB_ROOT_PASSWORD=secreto

[Service]
Restart=on-failure

[Install]
WantedBy=default.target
```

### Paso 3: Definir el Frontend (Nginx con dependencias)

Aquí es donde Quadlet brilla. En la sección `[Unit]` declaramos que no arranque si la BD no está lista.

```bash
nano ~/.config/containers/systemd/frontend.container
```

Contenido:

```ini
[Unit]
Description=Nginx Frontend
# Dependencias nativas de systemd
Requires=db.service
After=db.service

[Container]
Image=docker.io/library/nginx
ContainerName=frontend
Network=mired.network
PublishPort=8081:80

[Service]
Restart=on-failure

[Install]
WantedBy=default.target
```

### Paso 4: Despliegue del Stack Completo

```bash
# Recargar generador Quadlet
systemctl --user daemon-reload

# Iniciar ambos servicios (habilitándolos para que arranquen en el boot)
systemctl --user start db.service
systemctl --user start frontend.service
```

-----

## PARTE 4: Limpieza

La limpieza ahora es mucho más segura y elegante, ya que eliminamos los archivos de origen.

```bash
# 1. Parar los servicios
systemctl --user stop frontend.service db.service web.service

# 2. Borrar los archivos Quadlet
rm -f ~/.config/containers/systemd/*.container
rm -f ~/.config/containers/systemd/*.network

# 3. Recargar systemd para que elimine los servicios en memoria
systemctl --user daemon-reload

# 4. Limpiar contenedores y redes residuales (por si acaso)
podman system prune -af
```

-----

## PARTE 5: Conexión con entrega-1 (Playbook de Ansible)

Al completar esta práctica, el salto al primer hito (el entorno parametrizable de $N$ nodos balanceados) se vuelve trivial. El futuro Playbook de Ansible solo tendrá que:

1.  Asegurar dependencias (`podman`).
2.  Ejecutar `loginctl enable-linger`.
3.  Usar el módulo `ansible.builtin.copy` o `ansible.builtin.template` para lanzar estos pequeños archivos `.container` y `.network` a las carpetas `~/.config/containers/systemd/` de tus nodos.
4.  Usar el módulo `ansible.builtin.systemd` para recargar el *daemon* y hacer *start*.

Se debe organizar tu repositorio de la siguiente manera para que sea profesional y escalable:

    ansible-tfg/
    ├── inventory.ini          # Aquí defines tus N nodos
    ├── playbook.yml           # Flujo principal
    ├── roles/
    │   ├── common/            # Instalación de Podman y Linger
    │   ├── quadlets/          # Despliegue de .container y .network
    │   └── loadbalancer/      # Configuración del Nginx balanceador
    └── templates/
        ├── web.container.j2   # Plantilla para los workers
        └── lb.conf.j2         # Plantilla dinámica para el balanceador

**¡Ya no hace falta ejecutar y encadenar complejos scripts de Bash llenos de variables de entorno\! Todo es declarativo.**