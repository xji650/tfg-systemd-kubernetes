#!/bin/bash

# ==============================================================================
# ORQUESTADOR MAESTRO (HÍBRIDO): SYSTEMD VS KUBERNETES
# 1 Iteración de Infraestructura x 2 Iteraciones de Red x 4 Protocoloes
# ==============================================================================

set -e

# Configuración
WORKER_IPS=("192.168.98.143" "192.168.98.144")
WORKER_USER="littledragon"
BASE_DIR=$(pwd)
ITERACIONES_MAESTRAS=1

# Función para reiniciar nodos y esperar enfriamiento
reboot_and_wait() {
    echo "  -> Enviando señal de reinicio (Hard Reboot) a los nodos..."
    for IP in "${WORKER_IPS[@]}"; do
        ssh "${WORKER_USER}@${IP}" 'sudo reboot' > /dev/null 2>&1 || true
    done

    echo "  -> Esperando 60 segundos para el apagado..."
    sleep 60

    echo "  -> Comprobando disponibilidad (Ping / SSH)..."
    for IP in "${WORKER_IPS[@]}"; do
        until ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no "${WORKER_USER}@${IP}" 'echo "OK"' > /dev/null 2>&1; do
            sleep 5
        done
        echo "     [OK] Nodo $IP está online."
    done

    echo "  -> ENFRIAMIENTO TÉRMICO: Esperando 2 minutos para estabilizar CPU..."
    sleep 120
}

echo "========================================================="
echo " FASE 1: PREPARACIÓN Y TEST DE SYSTEMD + PODMAN"
echo "========================================================="

echo "Apagando y bloqueando Kubernetes (K3s) en nodos workers..."
for IP in "${WORKER_IPS[@]}"; do
    ssh "${WORKER_USER}@${IP}" 'sudo systemctl stop k3s-agent && sudo systemctl disable k3s-agent'
    ssh "${WORKER_USER}@${IP}" 'if [ -f /usr/local/bin/k3s-killall.sh ]; then sudo /usr/local/bin/k3s-killall.sh; fi'
done

for (( i=1; i<=ITERACIONES_MAESTRAS; i++ )); do
    echo -e "\n---> INICIANDO CICLO SYSTEMD: ITERACIÓN $i DE $ITERACIONES_MAESTRAS <---"
    reboot_and_wait
    
    cd "$BASE_DIR/systemd/1-infrastructure"
    ./generate_benchmarks.sh
    cd "$BASE_DIR"
done

echo -e "\n========================================================="
echo " FASE 2: TRANSICIÓN Y TEST DE KUBERNETES (K3S)"
echo "========================================================="

echo "Limpiando infraestructura de Podman/Systemd..."
cd "$BASE_DIR/systemd/1-infrastructure"
ansible-playbook -i inventory.ini clean.yml
cd "$BASE_DIR"

echo "Reviviendo el agente de Kubernetes (K3s)..."
for IP in "${WORKER_IPS[@]}"; do
    ssh "${WORKER_USER}@${IP}" 'sudo systemctl enable k3s-agent && sudo systemctl start k3s-agent'
done

for (( i=1; i<=ITERACIONES_MAESTRAS; i++ )); do
    echo -e "\n---> INICIANDO CICLO KUBERNETES: ITERACIÓN $i DE $ITERACIONES_MAESTRAS <---"
    reboot_and_wait
    
    cd "$BASE_DIR/kubernetes/1-infrastructure"
    ./generate_benchmarks.sh
    cd "$BASE_DIR"
done

echo -e "\n========================================================="
echo " FASE 3: EXTRACCIÓN DE DATOS Y COMPARATIVA"
echo "========================================================="

echo "Copiando y renombrando bases de datos CSV generadas..."
rm -f "$BASE_DIR/comparative/resultados_systemd.csv"
rm -f "$BASE_DIR/comparative/resultados_k3s.csv"

cp "$BASE_DIR/systemd/3-benchmarks-results/resultados_globales.csv" "$BASE_DIR/comparative/resultados_systemd.csv"
cp "$BASE_DIR/kubernetes/3-benchmarks-results/resultados_globales.csv" "$BASE_DIR/comparative/resultados_k3s.csv"

echo "[OK] CSVs listos. Generando gráficas finales..."
cd "$BASE_DIR/comparative"
python3 generar_comparativa.py
cd "$BASE_DIR"

echo -e "\n========================================================="
echo " PROCESO COMPLETADO EXITOSAMENTE "
echo " Gráficas disponibles en: $BASE_DIR/comparative/visualizations_final"
echo "========================================================="