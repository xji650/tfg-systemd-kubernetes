import csv
import os
from collections import defaultdict

# Rutas de archivos
CSV_PATH = "resultados_globales.csv"
MD_OUTPUT = "resultados-tablas.md"

if not os.path.exists(CSV_PATH):
    print(f"Error: No se encontró el archivo {CSV_PATH}. ¡Lanza primero el script de Bash!")
    exit(1)

# Diccionario para agrupar los datos por protocolo
datos_por_protocolo = defaultdict(lambda: defaultdict(list))

# 1. Leer el CSV y agrupar
with open(CSV_PATH, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        proto = row['Protocolo']
        for metrica in row.keys():
            if metrica not in ['Fecha', 'Protocolo']:
                datos_por_protocolo[proto][metrica].append(float(row[metrica]))

# 2. Generar el documento Markdown
md_content = "# Resultados Consolidados del Proyecto\n"
md_content += "> **Nota:** Estas tablas representan la **media histórica total** de todas las ejecuciones almacenadas en el Data Lake (`resultados-globales.csv`).\n\n"

for proto, metricas in datos_por_protocolo.items():
    # Calcular medias
    medias = {k: sum(v)/len(v) for k, v in metricas.items()}
    ejecuciones = len(metricas['T_deploy']) # Cuántas veces hemos probado este protocolo
    
    md_content += f"## Protocolo: {proto} (Basado en {ejecuciones} tests históricos)\n"
    md_content += "### Infraestructura\n"
    md_content += "| Métrica | Valor Promedio |\n|---|---|\n"
    md_content += f"| **T_deploy** | {medias['T_deploy']:.2f} s |\n"
    md_content += f"| **Recuperación (MTTR)** | {medias['MTTR']:.2f} ms |\n"
    md_content += f"| **CPU Reposo** | {medias['CPU_Reposo']:.2f} % |\n"
    md_content += f"| **RAM Reposo** | {medias['RAM_Reposo']:.2f} MB |\n\n"
    
    md_content += "### Rendimiento de Red (Estrés)\n"
    md_content += "| Métrica | Valor Promedio |\n|---|---|\n"
    md_content += f"| **T_Total** | {medias['T_Total']:.2f} s |\n"
    md_content += f"| **Throughput** | {medias['Throughput']:.2f} img/s |\n"
    md_content += f"| **Latencia RTT** | {medias['RTT']:.2f} ms |\n"
    md_content += f"| **T_Proc Worker** | {medias['T_Proc']:.2f} ms |\n"
    md_content += f"| **RAM Máxima** | {medias['RAM_Max']:.2f} MB |\n"
    md_content += f"| **CPU Máxima** | {medias['CPU_Max']:.2f} % |\n"
    md_content += f"| **Payload Red** | {medias['Payload_MB']:.2f} MB |\n\n"
    md_content += "---\n\n"

# 3. Guardar el archivo
with open(MD_OUTPUT, "w", encoding="utf-8") as f:
    f.write(md_content)

print(f"¡Éxito! Las tablas promediadas para tu TFG se han guardado en: {MD_OUTPUT}")