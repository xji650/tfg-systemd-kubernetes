#!/bin/bash

# ==============================================================================
# SCRIPT DE AUTOMATIZACIÓN: 1 DESPLIEGUE + 5 TESTS DE RED -> EXPORTACIÓN A CSV
# ==============================================================================

BASE_DIR=$(pwd)
WORKER_IPS=("192.168.98.143" "192.168.98.144")
WORKER_USER="littledragon"
SERVICE_NAME="worker.service"

PROTOCOLOS=(
    "../2-src-protocols/01-http-json"
    "../2-src-protocols/02-grpc-protobuf"
    "../2-src-protocols/03-zeromq-protobuf"
    "../2-src-protocols/04-zeromq-messagepack"
)

mkdir -p "$BASE_DIR/../3-benchmarks-results/raw_logs"

# NUESTRO NUEVO ARCHIVO BASE DE DATOS
CSV_FILE="$BASE_DIR/../3-benchmarks-results/resultados_globales.csv"

echo "========================================================="
echo " INICIANDO BENCHMARK AUTOMATIZADO (DATA LAKE / CSV)      "
echo "========================================================="

for PROTOCOLO in "${PROTOCOLOS[@]}"; do
    
    NOMBRE_PROTOCOLO=$(basename "$PROTOCOLO")
    DIR_RESULTADOS="$BASE_DIR/../3-benchmarks-results/raw_logs/$NOMBRE_PROTOCOLO"
    mkdir -p "$DIR_RESULTADOS"
    
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    FECHA_LEGIBLE=$(date +"%d/%m/%Y %H:%M:%S")
    LOG_FILE="$DIR_RESULTADOS/run_$TIMESTAMP.log"
    
    echo "=== BENCHMARK COMPLETO | INICIO: $FECHA_LEGIBLE ===" > "$LOG_FILE"
    echo -e "\n========================================================"
    echo " EVALUANDO PROTOCOLO: $NOMBRE_PROTOCOLO"
    echo "========================================================"

    # --- 1. INFRAESTRUCTURA (1 SOLA PASADA) ---
    echo "[1/4] Limpiando y desplegando Infraestructura..."
    echo -e "\n--- MÉTRICAS DE INFRAESTRUCTURA ---" >> "$LOG_FILE"
    
    ansible-playbook -i inventory.ini clean.yml > /dev/null
    
    START_TIME=$(date +%s.%N)
    ansible-playbook -i inventory.ini playbook.yml -e "experimento_path=$PROTOCOLO" > /dev/null
    END_TIME=$(date +%s.%N)
    
    DEPLOY_TIME=$(python3 -c "print(round($END_TIME - $START_TIME, 2))")
    echo "  [OK] T_deploy total: $DEPLOY_TIME segundos" | tee -a "$LOG_FILE"

    sleep 5

    for IP in "${WORKER_IPS[@]}"; do
        CONTAINER_ID=$(ssh $WORKER_USER@$IP "podman ps -q --filter name=worker-mnist")
        if [ -n "$CONTAINER_ID" ]; then
            # --- NUEVA MEDICIÓN (Global del Sistema Operativo) ---
            RAM_MB=$(ssh $WORKER_USER@$IP "free -m | awk '/^Mem:/{print \$3}'" 2>/dev/null)
            CPU_PERCENT=$(ssh $WORKER_USER@$IP "vmstat 1 2 | tail -1 | awk '{print 100 - \$15}'" 2>/dev/null)
            
            RAM_MB=${RAM_MB:-0}
            CPU_PERCENT=${CPU_PERCENT:-0}

            echo "  [OK] Nodo $IP - CPU Reposo (Global): $CPU_PERCENT% | RAM Reposo (Global): $RAM_MB MB" | tee -a "$LOG_FILE"
            
            # --- CHAOS TESTING (Medir recuperación de Systemd) ---
            ssh $WORKER_USER@$IP "
                START_REC=\$(date +%s.%N)
                podman kill $CONTAINER_ID > /dev/null
                while systemctl --user is-active --quiet $SERVICE_NAME; do sleep 0.05; done
                while ! systemctl --user is-active --quiet $SERVICE_NAME; do sleep 0.05; done
                END_REC=\$(date +%s.%N)
                REC_TIME_REAL=\$(python3 -c \"print(round(max(0, ((\$END_REC - \$START_REC) * 1000) - 3000), 2))\")
                echo '  [OK] Nodo $IP - Tiempo Real Arranque: '\$REC_TIME_REAL' ms'
            " | tee -a "$LOG_FILE"
        fi
    done

    echo -e "\n[2/4] Breve pausa antes de la prueba de red (5s)..."
    sleep 5

    # --- 2. BUCLE DE RED (5 ITERACIONES) ---
    echo "[3/4] Lanzando batería de 5 benchmarks de red..."
    cd "$BASE_DIR/$PROTOCOLO" || exit
    for RUN_N in {1..5}; do
        echo "  -> Ejecutando Test Red $RUN_N de 5..."
        echo -e "\n\n==================================================" >> "$LOG_FILE"
        echo " TEST RUN $RUN_N (Prueba de Estrés)" >> "$LOG_FILE"
        echo "==================================================" >> "$LOG_FILE"
        python3 master.py >> "$LOG_FILE" 2>&1
        sleep 3
    done
    cd "$BASE_DIR" > /dev/null

    # --- 3. EXTRACCIÓN A CSV (EL CEREBRO DE DATOS) ---
    echo "[4/4] Extrayendo datos y guardando en CSV..."
    python3 - "$LOG_FILE" "$CSV_FILE" "$NOMBRE_PROTOCOLO" "$FECHA_LEGIBLE" << 'EOF'
import sys, re, os

log_file = sys.argv[1]
csv_file = sys.argv[2]
protocol_name = sys.argv[3]
fecha = sys.argv[4]

def get_avg(filepath, pattern):
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        matches = re.findall(pattern, content)
        if not matches: return 0.0
        return sum([float(m) for m in matches]) / len(matches)
    except: return 0.0

# Extracción de Infraestructura
t_deploy = get_avg(log_file, r"T_deploy total:\s*([0-9\.]+)")
cpu_reposo = get_avg(log_file, r"CPU Reposo \(Global\):\s*([0-9\.]+)%")
# Podman suele devolver '15.2MB' o '15.2MiB', el regex coge el 15.2 perfecto
ram_reposo = get_avg(log_file, r"RAM Reposo \(Global\):\s*([0-9\.]+)")
mttr = get_avg(log_file, r"Tiempo Real Arranque:\s*([0-9\.]+)")

# Extracción de Red (Añadida la Tasa de Éxito)
t_total = get_avg(log_file, r"Tiempo Total \(s\):\s*([0-9\.]+)")
throughput = get_avg(log_file, r"Throughput \(img/s\):\s*([0-9\.]+)")
# Regex tolerante: Atrapa "Tasa Éxito" o "Tasa de Éxito"
tasa_exito = get_avg(log_file, r"Tasa(?: de)? Éxito \(%\):\s*([0-9\.]+)") 
rtt = get_avg(log_file, r"Latencia RTT Promedio \(ms\):\s*([0-9\.]+)")
t_proc = get_avg(log_file, r"Tiempo T_proc Promedio \(ms\):\s*([0-9\.]+)")
ram_max = get_avg(log_file, r"Pico Máx\. RAM Worker \(MB\):\s*([0-9\.]+)")
cpu_max = get_avg(log_file, r"CPU Promedio \(%\):\s*([0-9\.]+)")
payload_nodo = get_avg(log_file, r"Payload Promedio por Nodo \(MB\):\s*([0-9\.]+)")

# Escribir en CSV
file_exists = os.path.isfile(csv_file)
with open(csv_file, 'a', encoding='utf-8') as f:
    if not file_exists:
        f.write("Fecha,Protocolo,T_deploy,CPU_Reposo,RAM_Reposo,MTTR,T_Total,Throughput,Exito_%,RTT,T_Proc,RAM_Max,CPU_Max,Payload_MB\n")
        
    f.write(f"{fecha},{protocol_name},{t_deploy:.2f},{cpu_reposo:.2f},{ram_reposo:.2f},{mttr:.2f},{t_total:.2f},{throughput:.2f},{tasa_exito:.2f},{rtt:.2f},{t_proc:.2f},{ram_max:.2f},{cpu_max:.2f},{payload_nodo:.2f}\n")
EOF
    echo "[OK] Fila añadida a: $CSV_FILE"
done

ansible-playbook -i inventory.ini clean.yml > /dev/null
echo -e "\n========================================================="
echo " DATA LAKE ACTUALIZADO AL 100% "
echo "========================================================="