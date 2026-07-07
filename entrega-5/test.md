Esta es la hoja de ruta exacta y cronológica que debes seguir. Como has decidido empezar por Systemd, el paso más crítico de todos es **el primero**: asegurarnos de que Kubernetes esté totalmente "dormido" para que no te robe RAM mientras mides Systemd.

Sigue esta secuencia paso a paso para garantizar que tus datos sean 100% puros y válidos para tu TFG:

### FASE 1: Preparación y Test de Systemd + Podman

1. **1. Apagar y bloquear Kubernetes:** En los nodos (node-a y node-b).
Entra por SSH a tus nodos workers y detén el agente de K3s para que no consuma recursos de fondo:
sudo systemctl stop k3s-agent
sudo systemctl disable k3s-agent
(Si tienes el master en otro nodo, haz lo mismo con k3s allí para que la red se quede tranquila).


2. **2. Destruir rastros y reiniciar:** En los nodos.
Ejecuta sudo k3s-killall.sh (si lo tienes) para matar cualquier contenedor zombi de Kubernetes.
A continuación, haz un sudo reboot en los nodos. Esto vacía la memoria caché y asegura que el sistema operativo arranca limpio, solo con los procesos básicos de Linux.


3. **3. Enfriamiento y ejecución del Test Systemd:** En tu máquina Master.
Espera unos 2 minutos a que los nodos arranquen y las CPUs se enfríen al 0%.
Lanza tu script automatizado de bash para Systemd. Aquí es donde registrarás esos gloriosos ~150 MB de consumo base en tu CSV.


---

### FASE 2: Transición y Test de Kubernetes (K3s)

Una vez que el script de Systemd haya terminado sus 5 iteraciones y exportado los datos al CSV, procedemos al cambio de arquitectura.

1. **4. Limpiar la basura de Podman:** En tu máquina Master.
Asegúrate de que no queda nada del test anterior lanzando tu playbook de limpieza:
ansible-playbook -i inventory.ini clean.yml


2. **5. Revivir Kubernetes:** En los nodos.
Entra por SSH a tus nodos y vuelve a habilitar K3s para que tome el control del sistema operativo:
sudo systemctl enable k3s-agent


3. **6. Reinicio en frío (Hard Reboot):** En los nodos.
Ejecuta sudo reboot de nuevo en los nodos. 
Este reinicio es vital porque borrará cualquier caché en RAM que haya dejado el dataset de MNIST de PyTorch del test anterior, y obligará a K3s a reconstruir su red virtual (Flannel/Cilium) desde cero de forma limpia.


4. **7. Ejecución del Test Kubernetes:** En tu máquina Master.
Espera un par de minutos. Comprueba que tus nodos están listos ejecutando kubectl get nodes.
Lanza tu script automatizado de bash para Kubernetes. Aquí tu CSV registrará el verdadero peso de la orquestación (~600 MB) y su impacto en la latencia.


> **Nota para la defensa de tu TFG:** Documentar este proceso de "reinicio entre pruebas" en la memoria de tu proyecto suma muchísimos puntos. Demuestra que entiendes el concepto de **Thermal Throttling** (estrangulamiento térmico por CPU caliente) y la **contaminación por caché de RAM**, problemas típicos que arruinan los *benchmarks* de la gente que no tiene tu nivel de detalle.