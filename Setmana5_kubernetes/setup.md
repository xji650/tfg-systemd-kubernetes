Nodo padre `172.24.127.206`

Nodos hijos `192.168.98.143` y `192.168.98.144`

---

### 1. Instalar K3S (master):
```Bash
curl -sfL https://get.k3s.io | sh -
```

Para ver si está bien configurado

``` Bash
# Command 1: sudo k3s kubectl (The Built-In Version)
sudo k3s kubectl get node

# Command 2: sudo kubectl (The Standalone Version)
sudo kubectl get nodes
```

Si de usa Docker Desktop, y os falla `("Failed to start ContainerManager" err="system validation failed - wrong number of fields (expected 6, got 7)")`: 

1. Abrir Docker Desktop > Settings > Resources > WSL integration 

2. Marcar `Enable integration with my default WSL distro` 

3. En **Enable integration with additional distros**, activar `Ubuntu-22.04` o la version que tengais 

Y luego ejecuta:

```bash
sudo systemctl restart k3s
```
---

Para dejar de usar `sudo` cada vez que vamos a ejecutar:

```Bash
# 1. Create the default hidden folder for your user
mkdir -p ~/.kube

# 2. Copy the K3s config file into that new folder
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config

# 3. Give your user ownership of the file so you don't need sudo anymore
sudo chown $USER:$USER ~/.kube/config
```

Ahora, el kubectl independiente ya no es ciego. Intenta ejecutar este comando limpio (sin sudo, sin k3s):

```Bash
kubectl get nodes
```

---
### 2. Instalar K3S (worker):

```bash
curl -sfL https://get.k3s.io | K3S_URL=https://myserver:6443 K3S_TOKEN=mynodetoken sh -
```
- Substituye `myserver` por el `ip master`

    ```bash
    # En master:
    ip a
    ```

- El valor que se debe usar para `K3S_TOKEN` se almacena en `/var/lib/rancher/k3s/server/node-token` en el nodo del servidor (master).

    ```bash 
    sudo cat /var/lib/rancher/k3s/server/node-token
    ```

**Repetir el proceso en todos los nodos.**

---
### 3. Resultados

Para ver si esta bien configurado, ejecuta:

```Bash
kubectl get nodes
```

Deberia de salir el nodo **master** con `control-plane` y una lista con numeros de nodos **workers** configurados.

```    
NAME              STATUS   ROLES           AGE     VERSION
desktop-105rpfe   Ready    control-plane   3h21m   v1.35.4+k3s1
node-a            Ready    <none>          2m5s    v1.35.4+k3s1
node-b            Ready    <none>          6s      v1.35.4+k3s1
```