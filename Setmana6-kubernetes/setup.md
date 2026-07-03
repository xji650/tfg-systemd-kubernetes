# Instalacion y configuración de kubernetes K3S

Guía de instalación y configuración para un entorno Kubernetes ligero utilizando K3s.

## Arquitectura del Cluster
| Rol | Nombre/Etiqueta | IP |
| :--- | :--- | :--- |
| **Master** | Nodo Padre | `172.24.127.206` |
| **Worker 1** | Nodo Hijo A | `192.168.98.143` |
| **Worker 2** | Nodo Hijo B | `192.168.98.144` |

---

## 1. Instalación del Nodo Maestro (Master)

Ejecutar en el servidor `172.24.127.206`:

```bash
curl -sfL https://get.k3s.io | sh -
```

### Configuración de acceso sin `sudo`
Para gestionar el cluster con el `kubectl` independiente de tu usuario:

```bash
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $USER:$USER ~/.kube/config
```

### Inmovilización del entorno (Importante)
Para evitar actualizaciones automáticas que puedan romper la compatibilidad o los certificados TLS, ejecutamos el bloqueo de paquetes:

```bash
sudo apt-mark hold kubectl k3s podman conmon slirp4netns
```
> **Nota:** Esto asegura que `apt upgrade` ignore estos componentes. Para revertir, usar `unhold` en lugar de `hold`.

---

## 2. Instalación de Nodos Trabajadores (Workers)

### 1. Obtener el Token en el Master:

```bash
sudo cat /var/lib/rancher/k3s/server/node-token
```

### 2. Ejecutar en cada Nodo Hijo

Sustituyendo el `mynodetoken` e `myserver` (ip de master):
   
```bash
curl -sfL https://get.k3s.io | K3S_URL=https://myserver:6443 K3S_TOKEN=mynodetoken sh -
```

---

## ⚠️ Puntos Críticos y Solución de Errores

### Error de ContainerManager (Docker Desktop + WSL2)
Si aparece el error `system validation failed - wrong number of fields (expected 6, got 7)`, sigue estos pasos:
1. **Docker Desktop Settings** > Resources > WSL integration.
2. Activa `Enable integration with my default WSL distro`.
3. En **additional distros**, activa tu distribución (ej. `Ubuntu-22.04`).
4. Reinicia el servicio: `sudo systemctl restart k3s`.

### Persistencia de la IP
**IMPORTANTE:** Este cluster depende de que las IPs de los nodos sean estáticas.
* Si la IP del Master cambia, los nodos hijos perderán la conexión y los certificados TLS de `kubectl` fallarán.
* Se recomienda fijar la IP `172.24.127.206` en la configuración de red del sistema o en el router.

### Inmutabilidad de Aplicaciones
Para evitar que tus aplicaciones cambien sin previo aviso, **no uses el tag `:latest`** en tus archivos YAML. Usa siempre versiones fijas:
* NO: `image: nginx:latest`
* SÍ: `image: nginx:1.25.4`

---

## Verificación del Cluster

Desde el nodo Master, comprueba que todos los nodos están en estado `Ready`:
```bash
kubectl get nodes
```
Deberia de salir el nodo **master** con `control-plane` y una lista con numeros de nodos **workers** configurados.

**Resultado esperado:**
```    
NAME              STATUS   ROLES           AGE     VERSION
desktop-master    Ready    control-plane   3h      v1.X.X+k3s1
node-worker-a     Ready    <none>          2m      v1.X.X+k3s1
node-worker-b     Ready    <none>          1m      v1.X.X+k3s1
```