## FASE 1: Fundamentos y comparativa

# Semana 2: Gestión de Ciclo de Vida con systemd y Podman
![Podman](https://img.shields.io/badge/Podman-Rootless-892CA0?style=flat-square&logo=podman)
![Systemd](https://img.shields.io/badge/Systemd-Orchestration-darkgreen?style=flat-square&logo=linux)
![Semana](https://img.shields.io/badge/Semana-2-blue?style=flat-square)

## Objetivo

El objetivo es dominar la integración de **Podman** con **Systemd** a nivel de usuario (Rootless). Esto permite que los contenedores se comporten como servicios nativos del sistema operativo, garantizando su auto-recuperación ante fallos y su arranque automático sin intervención humana.

---

## PARTE 0: Requisito Previo Crítico: Habilitar "Linger" (Nodo A y B)

```bash
# Activar la persistencia
loginctl enable-linger $USER

# Verificar el estado
loginctl show-user $USER --property=Linger
```

Por defecto en Linux, cuando un usuario cierra su sesión SSH, todos sus procesos en segundo plano se destruyen. Además, los servicios propios del usuario no arrancan hasta que este hace *login*. 
El comando `enable-linger` cambia este comportamiento: le dice a `systemd` que inicie un gestor de servicios para este usuario desde el momento en que la máquina enciende (boot) y que no mate sus procesos al desconectarse. **Sin esto, ningún contenedor rootless sobrevivirá a un reinicio del servidor.**

Puedes verificar que está activo con: `ls /var/lib/systemd/linger/` (debería aparecer tu nombre de usuario).

Para desactivar la persistencia usa `loginctl disable-linger $USER`

---

## PARTE 1: Conceptos Systemd

**[Dónde ejecutar]:** En **Nodo A** (Exploración teórica).

```bash
systemctl --user status
journalctl --user -xe
```

**Explicación a fondo:**
* `systemctl`: Es el comando principal para controlar `systemd` (el gestor de servicios de Ubuntu).
* `--user`: **El concepto más importante de la semana.** Al usar Podman sin `sudo`, nuestros contenedores pertenecen a nuestro usuario estándar, no al administrador (`root`). Por tanto, debemos hablar con el `systemd` *del usuario*, no con el del sistema global.
* `journalctl`: Es el visor del diario (logs) del sistema. `-x` añade explicaciones a los errores y `-e` salta directamente al final (los eventos más recientes).

---

## PARTE 2: Pasos y configuración

*Nota: Para mantener la coherencia del clúster, desplegaremos el stack principal en el **Nodo A**. Puedes replicar exactamente los mismos comandos en el Nodo B si deseas tenerlo como respaldo.*

### Paso 1: Generación de Servicios Systemd

**[Dónde ejecutar]:** En **Nodo A**.

```bash
#Crear contenedor
podman run -d --name web -p 8080:80 docker.io/library/nginx

# Generar la Unidad de Servicio (.service)
podman generate systemd --name web --files --new
```

**Explicación a fondo:**
1. **`podman run`**: Lanzamos un contenedor efímero llamado `web` en segundo plano (`-d`).
2. **`podman generate systemd`**: Le pedimos a Podman que lea la configuración de ese contenedor en ejecución y la traduzca al idioma de `systemd`.
   * `--files`: En lugar de imprimir el resultado en pantalla, crea un archivo físico llamado `container-web.service` en la carpeta actual.
   * `--new`: **Parámetro vital.** Si no lo ponemos, `systemd` simplemente hará `podman start` del contenedor viejo. Al poner `--new`, configuramos el servicio para que, cada vez que arranque, destruya el contenedor anterior y lo cree *desde cero* utilizando la imagen base. Esto garantiza un entorno inmutable y limpio (evitando que el contenedor se corrompa con el tiempo).

---

### Paso 2: Instalación Rootless (Instalar el servicio)

**[Dónde ejecutar]:** En **Nodo A**.

```bash
# Ruta específica del servicio
mkdir -p ~/.config/systemd/user/
mv container-web.service ~/.config/systemd/user/

# Limpiar el contenedor
podman stop web && podman rm web

# Registrar y arrancar el servicio con systemd
systemctl --user daemon-reload
systemctl --user enable --now container-web.service
```

**Explicación a fondo:**
1. **`mkdir -p ...`**: Systemd de usuario solo lee servicios si están guardados en una ruta muy específica: `~/.config/systemd/user/`. Creamos la carpeta y movemos el archivo allí.
2. **`podman stop/rm`**: Borramos el contenedor manual que creamos el martes. A partir de ahora, solo systemd tiene permiso para crearlo.
3. **`daemon-reload`**: Le decimos a systemd: *"He metido un archivo nuevo en tu carpeta, recarga tu base de datos para que te des cuenta"*.
4. **`enable --now`**: Hace dos cosas. `enable` crea un enlace simbólico para que el servicio arranque automáticamente cuando el servidor se encienda. `--now` lo enciende en este mismo instante sin tener que esperar a reiniciar. Para solo arrancar sin persistencia, usa: `systemctl --user start container-web.service`.

---

### Paso 3: Resiliencia y Auto-reinicio (Chaos Testing)

**[Dónde ejecutar]:** En **Nodo A**.

```bash
podman kill web
watch -n 1 podman ps
```

**Explicación a fondo:**
Si abres el archivo `container-web.service` generado el martes, verás una línea que dice `Restart=always`. Esto significa que systemd está vigilando el PID (identificador de proceso) del contenedor.
* Usamos `podman kill` para simular que el contenedor ha sufrido un error fatal y se ha crasheado.
* `watch -n 1` ejecuta `podman ps` cada 1 segundo. Verás que, pasados unos segundos, el contenedor vuelve a aparecer mágicamente. Systemd detectó la caída y ejecutó las instrucciones para levantarlo de nuevo.

---

### Paso 4: Monitorización Avanzada (Telemetría Básica)
En el Edge, depurar problemas requiere acceder a los logs rápidamente. Olvídate de podman logs para servicios manejados por systemd; ahora el estándar es journalctl.

Para ver los logs en tiempo real de tu contenedor orquestado:

```Bash
journalctl --user -u container-web-edge.service -f`
```
(Pulsa Ctrl+C para salir).

---

## PARTE 3: Proyecto Stack (Web + DB en Red Aislada)

**[Dónde ejecutar]:** En **Nodo A**.

### Crear red (Opcional, ya que VM lo hace)
```bash
podman network create mi-red
```

### Servicio Base de datos (Redis, Mariadb, MySQL...)
```bash
#Crear contenedor
podman run -d --name db --network mi-red -e MARIADB_ROOT_PASSWORD=secreto docker.io/library/mariadb:10.11

# Generar la Unidad de Servicio (.service)
podman generate systemd --name db --files --new

# Ruta específica del servicio
mv container-db.service ~/.config/systemd/user/

# Limpiar el contenedor
podman stop db && podman rm db

# Registrar y arrancar el servicio con systemd
systemctl --user daemon-reload
systemctl --user enable --now container-db.service
```

### Servicio Web (Recordatorio: [despliegue db + web](#recordatorio-db--web))
```bash
#Crear contenedor
podman run -d --name frontend --network mi-red -p 8081:80 docker.io/library/nginx

# Generar la Unidad de Servicio (.service)
podman generate systemd --name frontend --files --new

# Ruta específica del servicio
mv container-frontend.service ~/.config/systemd/user/

# Opcional: configurar requiositos de db en la seccion [Unit] del .service. 
# Ver seccion: Recordatorio (db + web).

# Limpiar el contenedor
podman stop frontend && podman rm frontend

# Registrar y arrancar el servicio con systemd
systemctl --user daemon-reload
systemctl --user enable --now container-frontend.service
```

**Explicación a fondo:**
* **`network create`**: Crea un switch virtual aislado. Los contenedores dentro de esta red pueden encontrarse entre sí usando su nombre (`db` o `frontend`) como si fuera una dirección web (DNS interno).

* **`-e MARIADB...`**: Inyecta una variable de entorno requerida por la imagen de MariaDB para establecer la contraseña del administrador.

* **Nota de Seguridad:** Fíjate que el contenedor `db` NO tiene parámetro `-p`. Esto significa que la base de datos es totalmente inaccesible desde el exterior del servidor; solo el contenedor `frontend` (que comparte su red) puede hablar con ella.

### Recordatorio (db + web):

En un despliegue real, tu servidor Web (frontend) no debería arrancar si la base de datos (db) está apagada o fallando. Puedes enseñarle esto a `systemd` editando el archivo generado antes de recargarlo:

```Bash
vim ~/.config/systemd/user/container-frontend.service
```
En la sección [Unit], puedes declarar las dependencias de arranque de forma explícita:

```Ini, TOML
[Unit]
Description=Podman container-frontend.service
...
# Añade estas dos líneas:
Requires=container-db.service
After=container-db.service
```
Con este sencillo cambio, si reinicias la máquina, systemd esperará a que el contenedor de MariaDB esté en pie antes de lanzar el de NGINX.

---

## PARTE 4: Limpieza

```Bash
# 1. Parar todos los servicios antiguos (ignoramos errores si alguno no existe)
systemctl --user stop container-web.service container-db.service container-frontend.service || true

# 2. Deshabilitarlos para que no arranquen al reiniciar
systemctl --user disable container-web.service container-db.service container-frontend.service || true

# 3. Borrar todos los archivos de configuración de systemd generados por podman
rm -f ~/.config/systemd/user/container-*.service

# 4. Recargar systemd para que "olvide" los archivos borrados
systemctl --user daemon-reload

# 5. Parar y borrar absolutamente todos los contenedores huérfanos en Podman
podman stop -a && podman rm -a
```

---

## PARTE 4: Script de Automatización (`deploy.sh` y `clean.sh`)

**[Dónde ejecutar]:** En **Nodo B** (Para probar que el script levanta el stack entero de golpe de forma automática).

He empaquetado toda la teoría anterior en un script reproducible:

```bash
#!/bin/bash
# deploy.sh - Despliegue automatizado Stack Podman+Systemd

# 1. Aseguramos persistencia del usuario
loginctl enable-linger $USER

# 2. Creamos red y contenedores semilla
podman network create mi-red || true
podman run -d --name db --network mi-red -e MARIADB_ROOT_PASSWORD=secreto docker.io/library/mariadb:10.11
podman run -d --name web --network mi-red -p 8080:80 docker.io/library/nginx

# 3. Generamos los archivos de systemd (--new asegura inmutabilidad)
mkdir -p ~/.config/systemd/user/
podman generate systemd --name db --files --new
podman generate systemd --name web --files --new
sed -i '/^\[Unit\]/a Requires=container-db.service\nAfter=container-db.service' container-web.service
mv container-*.service ~/.config/systemd/user/

# 4. Destruimos las semillas manuales
podman stop db web && podman rm db web

# 5. Systemd toma el control
systemctl --user daemon-reload
systemctl --user enable --now container-db.service
systemctl --user enable --now container-web.service

echo "Despliegue completado. Systemd está ahora a cargo."
```

```bash
#!/bin/bash
# clean.sh - Limpieza total y eficiente del entorno Podman+Systemd

# 1. Parar y deshabilitar servicios antiguos (ignora errores si no existen)
systemctl --user stop container-{web,db}.service 2>/dev/null
systemctl --user disable container-{web,db}.service 2>/dev/null

# 2. Borrar las "recetas" (.service) generadas y recargar el demonio
rm -f ~/.config/systemd/user/container-*.service
systemctl --user daemon-reload

# 3. Forzar la parada y el borrado de todos los contenedores (-f fuerza, -a todos)
podman rm -fa 2>/dev/null

# 4. Eliminar la red virtual de forma forzada
podman network rm -f mi-red 2>/dev/null
```
---
