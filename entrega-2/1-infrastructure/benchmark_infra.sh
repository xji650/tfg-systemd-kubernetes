#!/bin/bash

# ==============================================================================
# SCRIPT DE AUTOMATIZACIÓN DE MÉTRICAS DE INFRAESTRUCTURA CON ANSIBLE
# ==============================================================================

# Añade aquí todas las IPs de tus nodos separados por un espacio
WORKER_IPS=("192.168.98.143" "192.168.98.144")
WORKER_USER="littledragon"
SERVICE_NAME="worker.service"

# 1. Definimos el array con los 4 protocolos a evaluar
PROTOCOLOS=(
    "../2-src-protocols/01-http-json"
    "../2-src-protocols/02-grpc-protobuf"
    "../2-src-protocols/03-zeromq-protobuf"
    "../2-src-protocols/04-zeromq-messagepack"
)

# Creamos la carpeta de logs si no existe
mkdir -p ../3-benchmarks-results/raw_logs

echo "========================================================="
echo " INICIANDO BENCHMARK AUTOMATIZADO DE INFRAESTRUCTURA     "
echo "========================================================="

# =========================================================
# BUCLE PRINCIPAL: Iterar sobre cada protocolo
# =========================================================
for PROTOCOLO in "${PROTOCOLOS[@]}"; do
    
    NOMBRE_PROTOCOLO=$(basename "$PROTOCOLO")
    LOG_FILE="../3-benchmarks-results/raw_logs/${NOMBRE_PROTOCOLO}_test.log"

    echo -e "\n========================================================"
    echo " 🚀 EVALUANDO PROTOCOLO: $NOMBRE_PROTOCOLO"
    echo "========================================================"

    # 0. Limpiamos el clúster (Fíjate que ya NO hay -K)
    echo "[0/6] Limpiando clúster..."
    ansible-playbook -i inventory.ini clean.yml > /dev/null

    # ---------------------------------------------------------
    # 1. MÉTRICA: Tiempo de Despliegue (T_deploy) Global
    # ---------------------------------------------------------
    echo "[1/6] Desplegando clúster (inyectando parámetro -e)..."
    START_TIME=$(date +%s.%N)

    # AQUÍ PONEMOS EL PARÁMETRO: -e "experimento_path=$PROTOCOLO"
    ansible-playbook -i inventory.ini playbook.yml -e "experimento_path=$PROTOCOLO" > /dev/null

    END_TIME=$(date +%s.%N)
    DEPLOY_TIME=$(python3 -c "print(round($END_TIME - $START_TIME, 2))")
    echo "  [OK] T_deploy total (Clúster): $DEPLOY_TIME segundos"

    sleep 5 # Damos 5 segundos para que los servicios se asienten bien

    # ---------------------------------------------------------
    # BUCLE: Evaluando cada nodo individualmente
    # ---------------------------------------------------------
    for IP in "${WORKER_IPS[@]}"; do
        echo -e "\n  ---> EVALUANDO NODO: $IP"
        
        CONTAINER_ID=$(ssh $WORKER_USER@$IP "podman ps -q --filter name=worker-mnist")

        if [ -z "$CONTAINER_ID" ]; then
            echo "  [ERROR] No se encontró contenedor en $IP."
            continue
        fi

        # 2. MÉTRICA: RAM y CPU en reposo
        echo "       [2/6] Midiendo RAM y CPU en reposo..."
        ssh $WORKER_USER@$IP "podman stats --no-stream --format '       [OK] CPU Reposo: {{.CPUPerc}} | RAM Reposo: {{.MemUsage}}' $CONTAINER_ID"

        # 3 y 4. MÉTRICA: Chaos Testing y Tiempo de Recuperación
        echo "       [3/6 y 4/6] Simulación de fallo y cronometrando recuperación..."
        ssh $WORKER_USER@$IP "
            START_REC=\$(date +%s.%N)
            podman kill $CONTAINER_ID > /dev/null
            
            while systemctl --user is-active --quiet $SERVICE_NAME; do sleep 0.05; done
            while ! systemctl --user is-active --quiet $SERVICE_NAME; do sleep 0.05; done
            
            END_REC=\$(date +%s.%N)
            REC_TIME_TOTAL=\$(python3 -c \"print(round((\$END_REC - \$START_REC) * 1000, 2))\")
            REC_TIME_REAL=\$(python3 -c \"print(round(max(0, ((\$END_REC - \$START_REC) * 1000) - 3000), 2))\")
            
            echo '       [OK] Tiempo Real de Arranque: '\$REC_TIME_REAL' ms (Total MTTR: '\$REC_TIME_TOTAL' ms)'
        "
    done

    echo -e "\n[5/6] Estabilizando clúster tras el Chaos Test..."
    sleep 5

    # ---------------------------------------------------------
    # 5. MÉTRICA: Prueba de Carga del Protocolo (master.py)
    # ---------------------------------------------------------
    echo "[6/6] Lanzando benchmark de red (master.py)..."
    cd "$PROTOCOLO" || exit
    
    # Ejecutamos tu código Python y guardamos el resultado
    python3 master.py > "../../3-benchmarks-results/raw_logs/${NOMBRE_PROTOCOLO}_test.log"
    
    cd - > /dev/null

    echo "✅ Pruebas de $NOMBRE_PROTOCOLO terminadas. Resultados guardados en: $LOG_FILE"

done

# ---------------------------------------------------------
# Borrar el contenedor para limpiar el entorno final
# ---------------------------------------------------------
echo -e "\n[!] Limpieza final de contenedores..."
ansible-playbook -i inventory.ini clean.yml > /dev/null

echo -e "\n========================================================="
echo " 🎉 BENCHMARK TOTAL FINALIZADO AL 100% "
echo "========================================================="