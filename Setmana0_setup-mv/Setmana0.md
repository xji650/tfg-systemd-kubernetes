## FASE 0: Setup

# Setmana 0: Arquitectura del Entorno de Pruebas 

![Podman](https://img.shields.io/badge/Podman-Rootless-892CA0?style=flat-square&logo=podman)
![Systemd](https://img.shields.io/badge/Systemd-Orchestration-darkgreen?style=flat-square&logo=linux)
![Semana](https://img.shields.io/badge/Semana-0-blue?style=flat-square)

## Objetivo

Desplegar un clúster simulado de dos nodos sobre un sistema anfitrión
Windows para la experimentación con técnicas de **prefetching en el
Edge**.

---

# 1. Aprovisionamiento de Nodos (Virtualización)

Para garantizar un entorno de red realista y soporte completo de
herramientas de control de tráfico (`tc`) y contenedores, se opta por
**virtualización pura**.

**Hipervisor:** VMware Workstation Player\
**Sistema Operativo:** Ubuntu Server 24.04 LTS (Sin GUI para
optimización de recursos)

### Recursos por Nodo

-   **vCPUs:** 2
-   **RAM:** 2 GB
-   **Almacenamiento:** 20 GB NVMe/SATA
-   **Networking:** Configuración en modo **Bridged (Adaptador Puente)**
    vinculado a la interfaz Wi‑Fi activa del anfitrión, permitiendo
    direccionamiento L2/L3 independiente.

---

# 2. Configuración de Identidad y Red

Se establecen identidades únicas para evitar colisiones en el clúster.

## 2.1 Direccionamiento Estático

Configuración realizada en:

    /etc/netplan/00-installer-config.yaml

**Nodo A (Activo)**

    IP: 192.168.1.101/24
    Gateway: 192.168.1.1

**Nodo B (Respaldo)**

    IP: 192.168.1.102/24
    Gateway: 192.168.1.1

---

## 2.2 Resolución Local de Nombres (en Nodo A y Nodo B)

Modificar el archivo:

    /etc/hosts

Contenido:

    127.0.0.1 localhost
    192.168.1.101 nodo-a
    192.168.1.102 nodo-b

Esto permite comunicación por **hostname** dentro del clúster.

---

## 2.3 Unicidad del Clon (Machine-ID)

Si se realiza un **Full Clone**, es obligatorio regenerar el
identificador único del sistema en el **Nodo B**.

    sudo truncate -s 0 /etc/machine-id
    sudo rm /var/lib/dbus/machine-id
    sudo ln -s /etc/machine-id /var/lib/dbus/machine-id
    sudo reboot

---

# 3. Herramientas de Ingeniería

## 3.1 Gestión de Contenedores y Versiones

Instalación de herramientas base para ejecutar el agente de
**prefetching**.

    sudo apt update
    sudo apt install -y git podman

### Verificación

    podman run hello-world

Esto confirma:

-   Aislamiento de **namespaces**
-   Conectividad de red
-   Funcionamiento del runtime de contenedores

---

## 3.2 Automatización SSH (Passwordless)

Configuración de acceso SSH mediante **intercambio de claves RSA** para permitir orquestación remota entre nodos.

### Generación de claves en Nodo A (y Nodo B)

    ssh-keygen -t rsa -b 4096 -N "" -f ~/.ssh/id_rsa

### En nodo A

#### 1. Copiar la clave pública al Nodo B

    ssh-copy-id littledragon@192.168.1.102

#### 2. Validación en Nodo A

    ssh nodo-b

### En nodo B

#### 1. Copiar la clave pública al Nodo A

    ssh-copy-id littledragon@192.168.1.101

#### 2 Validación en Nodo B

    ssh nodo-a

Debe acceder **sin solicitar credenciales**.

---
