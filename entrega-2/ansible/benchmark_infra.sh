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

ansible-playbook -i inventory.ini playbook.yml > /dev/null 2>&1

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
    
    # Calculamos el nombre exacto del contenedor gracias a tu Quadlet
    CONTAINER_NAME="worker-mnist-$IP"

    # ---------------------------------------------------------
    # 2. MÉTRICA: RAM y CPU en reposo
    # ---------------------------------------------------------
    echo "[2/4] Midiendo RAM y CPU en reposo..."
    ssh $WORKER_USER@$IP "podman stats --no-stream --format '  [OK] CPU Reposo: {{.CPUPerc}} | RAM Reposo: {{.MemUsage}}' $CONTAINER_NAME"

    # ---------------------------------------------------------
    # 3. MÉTRICA: Chaos Testing (Asesinato del proceso)
    # ---------------------------------------------------------
    echo "[3/4] Simulación de fallo (kill -9)..."
    ssh $WORKER_USER@$IP "
        PID=\$(podman inspect -f '{{.State.Pid}}' $CONTAINER_NAME)
        echo '  -> Matando proceso contenedor (PID: '\$PID')'
        kill -9 \$PID
    "

    # ---------------------------------------------------------
    # 4. MÉTRICA: Tiempo de Recuperación (T_recovery)
    # ---------------------------------------------------------
    echo "[4/4] Cronometrando recuperación de systemd..."
    ssh $WORKER_USER@$IP "
        START_REC=\$(date +%s.%N)
        
        while ! systemctl --user is-active --quiet $SERVICE_NAME; do
            sleep 0.1
        done
        
        END_REC=\$(date +%s.%N)
        REC_TIME=\$(python3 -c \"print(round((\$END_REC - \$START_REC) * 1000, 2))\")
        echo '  [OK] systemd revivió el servicio en: '\$REC_TIME' ms'
    "
done

echo -e "\n========================================================="
echo " BENCHMARK MULTINODO FINALIZADO "
echo "========================================================="