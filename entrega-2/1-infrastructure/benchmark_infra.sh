#!/bin/bash

# ==============================================================================
# SCRIPT DE AUTOMATIZACIÓN DE MÉTRICAS DE INFRAESTRUCTURA CON ANSIBLE
# ==============================================================================

# Añade aquí todas las IPs de tus nodos separados por un espacio
WORKER_IPS=("192.168.98.143" "192.168.98.144")
WORKER_USER="littledragon"
SERVICE_NAME="worker.service"

echo "========================================================="
echo " INICIANDO BENCHMARK AUTOMATIZADO DE INFRAESTRUCTURA     "
echo "========================================================="

# ---------------------------------------------------------
# 1. MÉTRICA: Tiempo de Despliegue (T_deploy) Global
# ---------------------------------------------------------
echo -e "\n[1/4] Lanzando Ansible y cronometrando T_deploy para todos los nodos..."
START_TIME=$(date +%s.%N)

ansible-playbook -i inventory.ini playbook.yml -K

END_TIME=$(date +%s.%N)
DEPLOY_TIME=$(python3 -c "print(round($END_TIME - $START_TIME, 2))")
echo "  [OK] T_deploy total (Clúster): $DEPLOY_TIME segundos"

# Damos 3 segundos para que los servicios se asienten bien
sleep 3

# =========================================================
# BUCLE: Evaluando cada nodo individualmente
# =========================================================
for IP in "${WORKER_IPS[@]}"; do
    echo -e "\n---------------------------------------------------------"
    echo " EVALUANDO NODO: $IP "
    echo "---------------------------------------------------------"
    
    # ---------------------------------------------------------
    # BÚSQUEDA DINÁMICA DEL CONTENEDOR
    # ---------------------------------------------------------
    # Obtenemos el ID real del contenedor filtrando por nombre
    CONTAINER_ID=$(ssh $WORKER_USER@$IP "podman ps -q --filter name=worker-mnist")

    # Verificamos si se encontró el contenedor
    if [ -z "$CONTAINER_ID" ]; then
        echo "  [ERROR] No se encontró ningún contenedor 'worker-mnist' corriendo en $IP."
        echo "          Asegúrate de que el playbook lo haya levantado correctamente."
        continue
    fi

    # ---------------------------------------------------------
    # 2. MÉTRICA: RAM y CPU en reposo
    # ---------------------------------------------------------
    echo "[2/4] Midiendo RAM y CPU en reposo..."
    ssh $WORKER_USER@$IP "podman stats --no-stream --format '  [OK] CPU Reposo: {{.CPUPerc}} | RAM Reposo: {{.MemUsage}}' $CONTAINER_ID"

    # ---------------------------------------------------------
    # 3 y 4. MÉTRICA: Chaos Testing y Tiempo de Recuperación
    # ---------------------------------------------------------
    echo "[3/4 y 4/4] Simulación de fallo y cronometrando recuperación..."
    ssh $WORKER_USER@$IP "
        START_REC=\$(date +%s.%N)
        
        # Usamos podman kill SIN la barra invertida para que pase el ID correcto
        echo '  -> Forzando caída del contenedor (Chaos Testing)...'
        podman kill $CONTAINER_ID > /dev/null
        
        # 1. Bucle para asegurar que systemd registra la caída (pasa a inactive/failed)
        while systemctl --user is-active --quiet $SERVICE_NAME; do
            sleep 0.05
        done
        
        # 2. Bucle para medir cuánto tarda en volver a estar active
        while ! systemctl --user is-active --quiet $SERVICE_NAME; do
            sleep 0.05
        done
        
        END_REC=\$(date +%s.%N)
        
        # Cálculo del Tiempo Total (MTTR)
        REC_TIME_TOTAL=\$(python3 -c \"print(round((\$END_REC - \$START_REC) * 1000, 2))\")
        
        # Cálculo del Tiempo Real (restando 3000 ms)
        REC_TIME_REAL=\$(python3 -c \"print(round(max(0, ((\$END_REC - \$START_REC) * 1000) - 3000), 2))\")
        
        # Impresión formateada para el TFG
        echo '  [OK] Tiempo Real de Arranque: '\$REC_TIME_REAL' ms (Tiempo Total MTTR: '\$REC_TIME_TOTAL' ms)'
    "
done

# ---------------------------------------------------------
# Borrar el contenedor para limpiar el entorno (opcional)
# ---------------------------------------------------------
echo -e "\n[5/5] Limpiando contenedores en cada nodo..."
ansible-playbook -i inventory.ini clean.yml

echo -e "\n========================================================="
echo " BENCHMARK MULTINODO FINALIZADO "
echo "========================================================="