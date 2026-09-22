import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 1. PREPARACIÓN DE DATOS
os.makedirs("visualizations_final", exist_ok=True)
sns.set_theme(style="whitegrid")

# Cargar ambos CSVs y añadirles la etiqueta de arquitectura
df_sys = pd.read_csv("resultados_systemd.csv")
df_sys['Arquitectura'] = 'Systemd (Nadiu)'

df_k3s = pd.read_csv("resultados_k3s.csv")
df_k3s['Arquitectura'] = 'Kubernetes (K3s)'

# Unir ambos mundos
df_total = pd.concat([df_sys, df_k3s])

# ==============================================================================
# EL FILTRO DEL OUTLIER
# Convertimos el outlier de Flannel a NaN SÓLO en la columna MTTR.
# Así Pandas divide el MTTR entre 9, pero usa los 10 valores para RAM y Throughput.
# ==============================================================================
df_total.loc[df_total['MTTR'] > 10000, 'MTTR'] = np.nan

# Sacar las medias por Protocolo y Arquitectura
df_avg = df_total.groupby(['Protocolo', 'Arquitectura']).mean(numeric_only=True).reset_index()

# Filtramos solo el protocolo ganador (ZeroMQ+MessagePack) para la batalla final
df_ganador = df_avg[df_avg['Protocolo'] == '04-zeromq-messagepack']


# ==============================================================================
# GRÁFICA 1: EL IMPUESTO ARQUITECTÓNICO (RAM EN REPOSO)
# ==============================================================================
plt.figure(figsize=(7, 5))
sns.barplot(data=df_ganador, x='Arquitectura', y='RAM_Reposo', palette=['#2c3e50', '#3498db'])
plt.title("L'\"Impost Arquitectònic\" a l'Edge\nConsum de RAM en Repòs (Overhead)", fontweight='bold')
plt.ylabel('RAM Consumida (MB)')
plt.xlabel('')

# Añadir el número exacto encima de la barra
for i, val in enumerate(df_ganador['RAM_Reposo']):
    plt.text(i, val + 10, f"{val:.0f} MB", ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig("visualizations_final/1_overhead_ram.png", dpi=300)
plt.close()

# ==============================================================================
# GRÁFICA 2: RESILIENCIA Y RECUPERACIÓN (MTTR)
# ==============================================================================
plt.figure(figsize=(7, 5))
sns.barplot(data=df_ganador, x='Arquitectura', y='MTTR', palette=['#e74c3c', '#e67e22'])
plt.title('Enginyeria del Caos (Resiliència)\nTemps Mitjà de Recuperació (MTTR)', fontweight='bold')
plt.ylabel('Mil·lisegons (ms) per recuperar-se')
plt.xlabel('')

for i, val in enumerate(df_ganador['MTTR']):
    plt.text(i, val + 20, f"{val:.0f} ms", ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig("visualizations_final/2_mttr_resiliencia.png", dpi=300)
plt.close()

# ==============================================================================
# GRÁFICA 3: RENDIMIENTO PURO (THROUGHPUT)
# ==============================================================================
plt.figure(figsize=(7, 5))
sns.barplot(data=df_ganador, x='Arquitectura', y='Throughput', palette=['#27ae60', '#2ecc71'])
plt.title('Penalització de Xarxa Virtual (SDN)\nThroughput (ZMQ + MessagePack)', fontweight='bold')
plt.ylabel('Imatges processades / segon')
plt.xlabel('')

for i, val in enumerate(df_ganador['Throughput']):
    plt.text(i, val + 100, f"{val:.0f} img/s", ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig("visualizations_final/3_throughput_comparativa.png", dpi=300)
plt.close()

print("¡Gráficas final generadas en la carpeta 'visualizations_final'!")