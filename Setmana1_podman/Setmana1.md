## FASE 1: Fundamentos y comparativa

# Semana1: Instalar herramientas y ejecutar el primer contenedor 

![Podman](https://img.shields.io/badge/Podman-Rootless-892CA0?style=flat-square&logo=podman)
![Systemd](https://img.shields.io/badge/Systemd-Orchestration-darkgreen?style=flat-square&logo=linux)
![Semana](https://img.shields.io/badge/Semana-1-blue?style=flat-square)

## Objetivo

Instalar herramientas y ejecutar el primer contenedor

# 1. Instalar Podman (node-a y node-b)

    sudo apt update && sudo apt install -y podman

# 2. Verificación contenedor hello-world (node-a y node-b)

Ejecuta podman la imagen del dockerHub (`docker.io/library/hello-world`) con interacción en terminal (`-it`) y borrar (`-rm`) la imagen una vez acabado la verificacion.  

    podman run -it --rm docker.io/library/hello-world

# 3. Contenedor nginx

A diferencia de Docker, Podman es más estricto por seguridad: no asume por defecto que quieres descargar cosas de Docker Hub. Para él, nginx es un "nombre corto" y no sabe si buscarlo en Docker Hub, Quay.io o en un registro privado.

## Opción 1 nombre completo (es la que uso):

### node-a

    podman run -d --name web -p 8080:80 docker.io/library/nginx

### node-b

    podman pull docker.io/library/nginx

## Opción 2 configura los registros (node-a y node-b): 

### 1. Edita el archivo de configuración (necesitas sudo):

    sudo nano /etc/containers/registries.conf

### 2. Busca la sección [registries.search] (o añádela al final si no existe) y déjala así:
    
    unqualified-search-registries = ["docker.io", "quay.io"]

### 3. Guarda (Ctrl+O, Enter) y sal (Ctrl+X).

### 4. Ejecutar tu comando

Podman te preguntará la primera vez de qué registro lo quieres o lo buscará directamente.

#### node-a

    podman run -d --name web -p 8080:80 nginx

### node-b

    podman pull nginx

# 4. Verificación contenedor nginx (node-a)

    http://192.168.1.101:8080/ 

# 5. Comandos básicos

    podman ps

    podman logs web

    podman stop web  

    podman rm web

    podman ps -a

    podman images 

    podman rmi hello-world

    podman pull docker.io/library/nginx

    podman stop $(podman ps -q)

    podman stop -a

    podman rm -a

-----

# 6. Análisis de Almacenamiento (OverlayFS)

Para entender cómo Podman gestiona las imágenes en el Edge, se ha analizado la estructura de capas de la imagen de Nginx.

    podman inspect nginx


## Conceptos clave:

* **LowerDir (Solo Lectura):** Son las capas base de la imagen (SO, librerías). Son inmutables y se comparten entre contenedores, lo que ahorra espacio en disco.

* **UpperDir (Escritura):** Capa efímera donde se guardan los cambios realizados mientras el contenedor está activo.

* **Importancia para el Prefetching:** Al hacer `podman pull` en el **Nodo B**, estamos descargando anticipadamente el **LowerDir**. Esto permite que el arranque tras un fallo sea casi instantáneo, ya que el grueso del software ya reside en el disco local del nodo de respaldo.

-----

# 7. Persistencia de Datos (Volúmenes)

Por defecto, los datos en la capa `UpperDir` se pierden al eliminar el contenedor. Para garantizar la continuidad en el Edge, se ha  implementado **Volúmenes**.

## 1. Preparación del Volumen

### a) Creación del volumen (Nodo A y B):
    podman volume create web-data
    podman volume ls  # Verifica la creacion

Nota: Se crea en ambos nodos para asegurar la simetría de la infraestructura, permitiendo que el Nodo B esté listo para recibir datos en el futuro.


### b) Ejecución con montaje de volumen (Nodo A):

    podman run -d --name web-persistente -v web-data:/usr/share/nginx/html:Z -p 8081:80 nginx

#### Desglose del comando:

- `-v web-data:/usr/share/nginx/html:Z`: Conecta el volumen de la VM con la ruta interna de Nginx. 

- La `:Z` gestiona los permisos de seguridad (SELinux).
    
## 2. Verificación de persistencia (Nodo A):

### a) Modifica la web:
    podman exec web-persistente sh -c "echo 'Hola desde el volumen persistente' > /usr/share/nginx/html/index.html"

### b) Verifica en el navegador:

Entra en `192.168.1.101:8081` y verás tu mensaje.

### c) Borrar contenedor: 
    podman stop web-persistente 
    podman rm web-persistente 

### d) Crea uno nuevo con el mismo volumen:

Se crea un nuevo contenedor (web-nuevo) vinculado al mismo volumen

    podman run -d --name web-nuevo -v web-data:/usr/share/nginx/html:Z -p 8081:80 nginx

### e) Resultado: 

Entra en `192.168.1.101:8081` y verás el mensaje seguirá ahí.

-----

# 8. Configuración Dinámica (Variables de Entorno)

Para evitar crear una imagen distinta para cada nodo, utilizamos variables de entorno para personalizar el comportamiento del software.

```bash
podman run -d --name web-env -e "NODO=NODO-A" -p 8082:80 nginx
```

`-e`: Sirve para pasar configuración (como el nombre del nodo) al software sin tener que cambiar los archivos internos.