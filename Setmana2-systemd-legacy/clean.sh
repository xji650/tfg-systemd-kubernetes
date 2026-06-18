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