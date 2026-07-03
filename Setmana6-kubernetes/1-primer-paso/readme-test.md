# Desplegar primer archivo `.yaml` en kubernestes

## 1. **Crea el archivo de prueba:**
En tu nodo Master, crea un archivo llamado `test.yaml` y pega este contenido.
*Fíjate que en un mismo archivo estamos definiendo el Deployment (los contenedores) y el Service (la red), separados por `---`.*

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: test-deployment
spec:
  replicas: 3 # Pedimos 3 copias para forzar el reparto en los nodos
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: nginx
        image: nginx:1.25.4 # Aplicamos tu regla de inmutabilidad
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: test-service
spec:
  type: NodePort
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 80
    nodePort: 30080 # Forzamos a que se abra este puerto en las IPs de todos los nodos
```


## 2. **Lanza el despliegue al clúster:**
Aplica la configuración con tu "mando a distancia":

```bash
kubectl apply -f test.yaml
```

Retorna:

```
deployment.apps/test-deployment created
service/test-service created
```


## 3. **Comprueba la distribución en los Workers:** El comando clave.
Para ver dónde han caído los pods, usa este comando añadiendo el flag `-o wide`. Esto le dice a K8s que te muestre columnas extra, incluyendo en qué nodo exacto se está ejecutando cada pod:

```bash
kubectl get pods -o wide
```

Retorna:

```
NAME                               READY   STATUS    RESTARTS   AGE    IP          NODE              NOMINATED NODE   READINESS GATES
test-deployment-84c8bf58dd-pgmn6   1/1     Running   0          114s   10.42.0.9   desktop-105rpfe   <none>           <none>
test-deployment-84c8bf58dd-vmdg9   1/1     Running   0          114s   10.42.0.8   desktop-105rpfe   <none>           <none>
test-deployment-84c8bf58dd-wnmcm   1/1     Running   0          114s   10.42.0.7   desktop-105rpfe   <none>           <none>
```

*Lo ideal es que veas que tus pods están repartidos entre `node-worker-a` y `node-worker-b`. Si todos se quedan en "Pending" o dan error, tenemos un problema de comunicación entre el Master y los hijos.*


## 4. **La prueba de fuego (Red externa):**
Como configuramos un `NodePort` en el puerto `30080`, Kubernetes abre ese puerto mágicamente en **todas** las IPs de tus nodos (incluso en los que no tienen el pod ejecutándose).

Desde tu ordenador, abre el navegador web y pon la IP de cualquiera de tus Workers con ese puerto. Por ejemplo:
`[http://192.168.98.143:30080](http://192.168.98.143:30080)`

Si ves la pantalla de *Welcome to nginx!*, ¡felicidades! Tu clúster está 100% operativo y enrutando tráfico correctamente.


## 5. **Limpia la zona de pruebas:**
Una vez que hayas comprobado que funciona, borra todo lo que hemos creado para dejar el clúster limpio de cara al despliegue real de tu TFG:

```bash
kubectl delete -f test.yaml
```
Retorna:

```
deployment.apps "test-deployment" deleted from default namespace
service "test-service" deleted from default namespace
```

---

> **Nota de experto:** En producción real rara vez se usa `NodePort` porque te obliga a recordar puertos raros (como el 30080). Lo normal es usar dominios web (ej. `mi-tfg.local`) apuntando al puerto 80 estándar. La ventaja de K3s es que ya trae un gestor para esto instalado por defecto llamado **Traefik (Ingress Controller)**.