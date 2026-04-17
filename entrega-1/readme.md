# Pasos para la ejecución y validación

## FASE 0: Instalación

Asegúrate de tener Ansible instalado en tu máquina anfitriona o en una VM de gestión.

```bash
# Actualizar el sistema y preparar repositorios
sudo apt update
sudo apt install software-properties-common

#Añadir el repositorio oficial de Ansible
sudo add-apt-repository --yes --update ppa:ansible/ansible

#Instalar Ansible
sudo apt install ansible -y
```


## Fase 1: Forjar la "Llave Maestra" en tu WSL

Lo primero es crear una nueva identidad (llave SSH) exclusiva para tu máquina de control.

1. **Genera la llave:**
   Ejecuta el siguiente comando en tu terminal de Ubuntu:
   ```bash
   ssh-keygen -t rsa -b 4096
   ```
2. **Acepta todo por defecto:**
   El sistema te hará tres preguntas (dónde guardarla y si quieres ponerle contraseña). **Pulsa `Enter` tres veces seguidas** sin escribir nada. Esto creará una llave sin contraseña, indispensable para que Ansible pueda automatizar sin pedirte que teclees nada.

---

## Fase 2: Repartir las "Cerraduras" a los Nodos Edge

Ahora vamos a enviar la llave pública (la cerradura) a tus máquinas virtuales. Durante este paso, te pedirá la contraseña del usuario `littledragon` por última vez.

1. **Instala la llave en el Nodo A (192.168.1.101):**
   ```bash
   ssh-copy-id littledragon@192.168.1.101
   ```
   *(Si te pregunta `Are you sure you want to continue connecting?`, escribe `yes` y pulsa Enter. Luego, mete la contraseña de littledragon).*

2. **Instala la llave en el Nodo B (192.168.1.102):**
   ```bash
   ssh-copy-id littledragon@192.168.1.102
   ```

3. **Prueba de fuego (Verificación):**
   Intenta entrar al Nodo B desde tu WSL:
   ```bash
   ssh littledragon@192.168.1.102
   ```
   Si entras directamente sin que te pida contraseña, ¡lo has conseguido! Escribe `exit` para volver a tu WSL.

---

## Fase 3: Preparar el Proyecto en WSL (Aviso Crítico de Windows)

Aquí hay una trampa muy común al usar WSL con Ansible: **Los permisos de archivos.**
Si tienes tus archivos de Ansible guardados en tu escritorio de Windows (por ejemplo en `/mnt/c/Users/TuUsuario/Desktop/...`), Ansible **va a fallar** por razones de seguridad, ya que considera que el sistema de archivos de Windows es "inseguro" para guardar llaves e inventarios.

Tus archivos deben vivir en el sistema de archivos de Linux (la "casita" `~`).

1. **Crea una carpeta en tu WSL para el proyecto:**
   ```bash
   mkdir ~/tfg-ansible
   cd ~/tfg-ansible
   ```
2. **Recrea aquí tus archivos y carpetas:**
   Si no los tienes aquí, crea la estructura rápidamente usando `nano`. Debes tener exactamente esto dentro de `~/tfg-ansible`:
   * `inventory.ini`
   * `playbook.yml`
   * `group_vars/all.yml`
   * `templates/red.network.j2`
   * `templates/web.container.j2`
   * `templates/nginx-lb.conf.j2`
   * `templates/lb.container.j2`

*(Puedes usar `nano inventory.ini`, pegar el texto, hacer `Ctrl+O`, `Enter`, `Ctrl+X`. Repite con todos los archivos que repasamos en el mensaje anterior).*

---

## Fase 4: Ejecución de prueba

Ya tienes a tu Director de Orquesta con acceso VIP a los nodos y tu partitura (los archivos YAML y plantillas) en el lugar seguro de Linux.

Asegúrate de estar en la carpeta correcta:
```bash
cd ~/tfg-ansible
```

Y lanza el misil de la automatización:
```bash
ansible-playbook -i inventory.ini playbook.yml -K
```

Verás cómo Ansible se conecta, crea las redes, levanta los workers, configura el Nginx temporal, lanza el balanceador y deja todo listo en cuestión de segundos. Cuando termine, abre tu navegador en Windows y entra a `http://192.168.1.101` para ver tu clúster balanceando el tráfico.

Ahora verifica que realmente funciona:

```bash
# ¿El balanceador responde?
curl http://192.168.1.101:8888

# Llámalo varias veces para ver el round-robin entre workers
curl http://192.168.1.101:8888
curl http://192.168.1.101:8888
curl http://192.168.1.101:8888
```

Deberías ver alternar:
```
Hola! Estas siendo atendido por el worker: node-a
Hola! Estas siendo atendido por el worker: node-b
```
**Prueba de Resiliencia**: Apaga el **Nodo B** (`sudo reboot`). Vuelve a hacer `curl` al balanceador. El sistema debe seguir respondiendo a través del **Nodo A** sin intervención manual.

```bash
# Apaga node-b
ssh  -t littledragon@192.168.1.102 "sudo reboot"

# Sigue respondiendo solo con node-a?
curl http://192.168.1.101:8888

# Cuando node-b vuelva, ¿arranca solo el contenedor sin intervención?
# (espera 1 min y prueba de nuevo)
curl http://192.168.1.101:8888
```

## Fase 5: Limpieza

```bash
ansible-playbook -i inventory.ini clean.yml -K
```

---