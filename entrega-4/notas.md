- porque cnn y no mlp

- que es train loss y validation loss

- porque hay train loss y no hay validation loss

- como se ha hecho la grafica del train loss(por lotes)

- porque solo una epoca

- relacion de una sola epoca y pbtencion de validation loss

- como sabe si la ia ha memorizado o ha aprendido

- cuantos tipos de envío de datos o informacion existe

- porque el modelo se envia por la red usando protocolos y no por junto con la imagen del docker

---

El problema del "Impuesto Arquitectónico" (Métricas Injustas)

El Problema: Al principio, para medir el consumo de recursos en reposo (Idle), usábamos podman stats y kubectl top. Esto era un error metodológico, porque esas herramientas solo miden lo que consume el contenedor por dentro. Hacía parecer que Kubernetes y Systemd consumían la misma RAM, ocultando todo el peso de la plataforma que corre de fondo.

El Cambio: Cambiamos el enfoque para medir el nodo completo a nivel de Sistema Operativo. Introdujimos comandos nativos de Linux (free -m y vmstat) a través de SSH.

Qué decirle al tribunal: "Nos dimos cuenta de que medir solo el contenedor sesgaba los datos a favor de Kubernetes. Para ser justos y capturar el 'overhead' real de la orquestación en el Edge, pasamos a medir el sistema operativo global. Así demostramos que K3s reserva ~600MB solo por existir, frente a los ~150MB de Systemd."

---

Contaminación Cruzada y Contenedores Fantasma

El Problema: Al alternar las pruebas de Podman a K3s (y viceversa), nos encontramos con "servicios zombie" (como contenedores Nginx que revivían solos) y consumo de RAM fantasma. K3s dejaba procesos containerd enganchados, y Podman revivía contenedores debido al Restart=always y la persistencia de usuario de Systemd.

El Cambio: Diseñamos un Protocolo de Transición Estricto. Implementamos apagados de servicios de fondo (sudo systemctl stop k3s-agent), purgas destructivas (podman system prune -a -f, k3s-killall.sh), gestión del linger de sesión (loginctl enable-linger), y lo más importante: un reinicio en frío (sudo reboot) entre arquitecturas.

Qué decirle al tribunal: "Para garantizar el rigor científico, establecí un protocolo de limpieza y reinicio en frío ('Hard Reboot') entre las pruebas de distintas arquitecturas. Esto era vital por dos motivos: primero, para evitar que demonios en segundo plano (como containerd) contaminaran el consumo de RAM; y segundo, para limpiar la caché de RAM y evitar el Thermal Throttling (estrangulamiento térmico de la CPU) que falsearía los tiempos de inferencia en las iteraciones finales."

---
