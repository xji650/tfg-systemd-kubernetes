#!/bin/bash

# ==============================================================================
# SCRIPT DE AUTOMATIZACIÓN TOTAL: 5 ITERACIONES + INFRAESTRUCTURA
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
echo " INICIANDO BENCHMARK AUTOMATIZADO (5 ITERACIONES)        "
echo "========================================================="

# =========================================================
# BUCLE PRINCIPAL: Iterar sobre cada protocolo
# =========================================================
for PROTOCOLO in "${PROTOCOLOS[@]}"; do
    
    NOMBRE_PROTOCOLO=$(basename "$PROTOCOLO")
    
    # Creamos una carpeta específica para cada protocolo para no mezclar nada
    DIR_RESULTADOS="../3-benchmarks-results/raw_logs/$NOMBRE_PROTOCOLO"
    mkdir -p "$DIR_RESULTADOS"
    
    # Archivo donde guardaremos los datos de CPU, RAM y T_deploy (Solución al Punto 1)
    INFRA_LOG="$DIR_RESULTADOS/00_infraestructura.log"
    echo "=== MÉTRICAS DE INFRAESTRUCTURA: $NOMBRE_PROTOCOLO ===" > "$INFRA_LOG"

    echo -e "\n========================================================"
    echo " 🚀 EVALUANDO PROTOCOLO: $NOMBRE_PROTOCOLO"
    echo "========================================================"

    # 0. Limpiamos el clúster (Fíjate que ya NO hay -K)
    echo "[0/6] Limpiando clúster..."
    ansible-playbook -i inventory.ini clean.yml > /dev/null

    # ---------------------------------------------------------
    # 1. MÉTRICA: Tiempo de Despliegue (T_deploy) Global
    # ---------------------------------------------------------
    echo -e "\n[1/6] Desplegando clúster..."
    START_TIME=$(date +%s.%N)

    # AQUÍ PONEMOS EL PARÁMETRO: -e "experimento_path=$PROTOCOLO"
    ansible-playbook -i inventory.ini playbook.yml -e "experimento_path=$PROTOCOLO" > /dev/null

    END_TIME=$(date +%s.%N)
    DEPLOY_TIME=$(python3 -c "print(round($END_TIME - $START_TIME, 2))")
    
    # Guardamos en pantalla y en el log
    echo "  [OK] T_deploy total: $DEPLOY_TIME segundos" | tee -a "$INFRA_LOG"

    sleep 5

    # ---------------------------------------------------------
    # BUCLE: Evaluando cada nodo individualmente
    # ---------------------------------------------------------
    for IP in "${WORKER_IPS[@]}"; do
        echo -e "\n  ---> EVALUANDO NODO: $IP" | tee -a "$INFRA_LOG"
        
        CONTAINER_ID=$(ssh $WORKER_USER@$IP "podman ps -q --filter name=worker-mnist")

        if [ -z "$CONTAINER_ID" ]; then
            echo "  [ERROR] No se encontró contenedor en $IP." | tee -a "$INFRA_LOG"
            continue
        fi

        # 2. MÉTRICA: RAM y CPU en reposo
        echo "       [2/6] Midiendo RAM y CPU en reposo..."
        ssh $WORKER_USER@$IP "podman stats --no-stream --format '       [OK] CPU Reposo: {{.CPUPerc}} | RAM Reposo: {{.MemUsage}}' $CONTAINER_ID" | tee -a "$INFRA_LOG"

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
            
            echo '       [OK] Tiempo Real Arranque: '\$REC_TIME_REAL' ms (Total MTTR: '\$REC_TIME_TOTAL' ms)'
        " | tee -a "$INFRA_LOG"
    done

    # Damos 10 segundos en lugar de 5 para asegurar que el nodo se enfría tras el caos
    echo -e "\n[5/6] Enfriando clúster tras el Chaos Test (10s)..."
    sleep 10

    # ---------------------------------------------------------
    # 5. BUCLE DE 5 ITERACIONES PARA LA PRUEBA DE RED (ESTRÉS)
    # ---------------------------------------------------------
    echo "[6/6] Lanzando batería de 5 benchmarks de red (Prueba de Estrés)..."
    
    cd "$PROTOCOLO" || exit
    
    for RUN in {1..5}; do
        echo "  -> Ejecutando Test $RUN de 5..."
        
        LOG_DESTINO="../../3-benchmarks-results/raw_logs/$NOMBRE_PROTOCOLO/run_$RUN.log"
        
        echo -e "\n\n==================================================" >> "$LOG_DESTINO"
        echo " NUEVA EJECUCIÓN DEL TEST " >> "$LOG_DESTINO"
        echo "==================================================" >> "$LOG_DESTINO"
        
        python3 master.py >> "$LOG_DESTINO" 2>&1
        
        sleep 3
    done
    
    cd - > /dev/null

    echo "Pruebas de $NOMBRE_PROTOCOLO terminadas. Resultados guardados en: $DIR_RESULTADOS"

done

# ---------------------------------------------------------
# Borrar el contenedor para limpiar el entorno final
# ---------------------------------------------------------
echo -e "\n[!] Limpieza final de contenedores..."
ansible-playbook -i inventory.ini clean.yml > /dev/null

echo -e "\n========================================================="
echo " 🎉 BENCHMARK TOTAL FINALIZADO AL 100% "
echo "========================================================="