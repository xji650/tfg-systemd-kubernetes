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