import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker
import os

# ==============================================================================
# CONFIGURACIÓN GLOBAL PROFESIONAL
# ==============================================================================
CSV_PATH = "resultados_globales.csv"
OUTPUT_DIR = "./visualizations" # Carpeta donde caerán los gráficos

# Creamos la carpeta de salida si no existe
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Configurar el estilo visual predeterminado de la industria (blanco y limpio)
sns.set_theme(style="whitegrid")
# Usar una paleta de colores corporativa y clara (Deep, viridis, etc.)
palette = sns.color_palette("viridis", 4) 

# Diccionario para limpiar los nombres de los protocolos en los gráficos
CLEAN_NAMES = {
    '01-http-json': 'HTTP/JSON',
    '02-grpc-protobuf': 'gRPC/Proto',
    '03-zeromq-protobuf': 'ZMQ/Proto',
    '04-zeromq-messagepack': 'ZMQ/MsgPack'
}

# ==============================================================================
# 1. CARGA Y PROCESAMIENTO HISTÓRICO DE DATOS (DATA SCIENCE)
# ==============================================================================
print(f"Leyendo Data Lake histórico: {CSV_PATH}...")

if not os.path.exists(CSV_PATH):
    print(f"Error: No se encontró {CSV_PATH}. ¡Lanza tests primero!")
    exit(1)

# Leer CSV completo
df_crudo = pd.read_csv(CSV_PATH)

# Calcular MEDIAS HISTÓRICAS por Protocolo (Data Science real)
# Igual que en el script .py anterior, agrupamos todo el pasado y sacamos media.
df_avg = df_crudo.groupby('Protocolo').mean(numeric_only=True).reset_index()

# Limpiar nombres de protocolos para el gráfico (Ej: HTTP/JSON en lugar de 01-http-json)
df_avg['Protocolo_Limpio'] = df_avg['Protocolo'].map(CLEAN_NAMES)

print(f"[OK] Datos consolidados históricamente para {len(df_avg)} protocolos.")


# ==============================================================================
# 2. GRÁFICO 1: EL TITULAR - Rendimiento Global (Throughput)
# ==============================================================================
print("Generando Gráfico 1: Throughput Comparativo...")

# Crear figura (ancho, alto en pulgadas)
plt.figure(figsize=(10, 6))

# Gráfico de barras simple (X=Protocolo, Y=Throughput)
ax1 = sns.barplot(
    data=df_avg, 
    x='Protocolo_Limpio', 
    y='Throughput', 
    palette="viridis",
    edgecolor="0.3" # Borde fino para profesionalidad
)

# Estética Profesional
plt.title('Rendimiento Global del Sistema (Image Throughput)', fontsize=16, pad=20, fontweight='bold')
plt.xlabel('Protocolo de Comunicación (Edge-to-Edge)', fontsize=12, labelpad=15)
plt.ylabel('Rendimiento Promedio (imágenes/segundo)', fontsize=12, labelpad=15)

# Formatear el eje Y para mostrar 'K' en lugar de miles (Ej: 80.000 -> 80K)
ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f'{x/1000:.0f}K'))

# Guardar
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/graph_1_throughput.png", dpi=300) # dpi=300 es calidad de imprenta
plt.close() # Liberar memoria


# ==============================================================================
# 3. GRÁFICO 2: EL "EDGE" - Consumo de RAM (Reposo vs Pico)
# ==============================================================================
print("Generando Gráfico 2: Trade-off de Memoria RAM (Edge Device)...")

# Para gráficos agrupados (seaborn prefiere formato 'largo'), tenemos que transformar la tabla
df_ram_long = df_avg.melt(
    id_vars='Protocolo_Limpio', 
    value_vars=['RAM_Reposo', 'RAM_Max'],
    var_name='Estado_RAM', 
    value_name='RAM_MB'
)

# Limpiar nombres de estado (RAM_Reposo -> Estado: Reposo)
df_ram_long['Estado_RAM'] = df_ram_long['Estado_RAM'].map({'RAM_Reposo': 'Reposo', 'RAM_Max': 'Pico de Carga (Estrés)'})

# Crear figura
plt.figure(figsize=(11, 6))

# Gráfico de barras agrupadas (HUE es la variable que agrupa)
ax2 = sns.barplot(
    data=df_ram_long,
    x='Protocolo_Limpio',
    y='RAM_MB',
    hue='Estado_RAM',
    palette=['#A2D2FF', '#0077B6'], # Azul suave vs Azul corporativo intenso
    edgecolor="0.3"
)

# Estética Profesional
plt.title('Huella de Memoria RAM por Protocolo (Edge Node Context)', fontsize=16, pad=20, fontweight='bold')
plt.xlabel('Protocolo', fontsize=12, labelpad=15)
plt.ylabel('Consumo de RAM Promedio (MB)', fontsize=12, labelpad=15)

# Ajustar leyenda profesional
plt.legend(title='Estado del Contenedor', title_fontsize='11', fontsize='10', frameon=True)

# Añadir una línea roja discontinua que represente el límite crítico para tu TFG (Ej: 1GB)
plt.axhline(y=1000, color='r', linestyle='--', alpha=0.6, label='Límite Crítico Propuesto (1GB)')

plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/graph_2_ram_footprint.png", dpi=300)
plt.close()


# ==============================================================================
# 4. GRÁFICO 3: EL INGENIERO SENIOR - Scatter Plot (Latencia vs Throughput)
# ==============================================================================
print("Generando Gráfico 3: Matriz de Trade-off (Latencia vs Rendimiento)...")

plt.figure(figsize=(10, 7))

# Gráfico de dispersión (Scatter). X=Latencia RTT, Y=Throughput. Hue identifica el "puntito".
ax3 = sns.scatterplot(
    data=df_avg,
    x='RTT', 
    y='Throughput', 
    hue='Protocolo_Limpio',
    style='Protocolo_Limpio', # Forma distinta por protocolo para dalónicos
    palette="viridis",
    s=250, # Tamaño gigante del "puntito"
    edgecolor="0.2",
    linewidth=1.5,
    alpha=0.85 # Ligera transparencia
)

# --- MAGIA SENIOR: Etiquetar los puntos automáticamente ---
# Para que el tribunal no tenga que mirar la leyenda, escribimos el nombre AL LADO de cada punto
for i in range(df_avg.shape[0]):
    text = df_avg.iloc[i]['Protocolo_Limpio']
    x_pos = df_avg.iloc[i]['RTT']
    y_pos = df_avg.iloc[i]['Throughput']
    
    # Ajuste fino de la etiqueta (un poco a la derecha y arriba del punto)
    plt.text(
        x_pos + (df_avg['RTT'].max()*0.02), # Pequeño offset en X
        y_pos + (df_avg['Throughput'].max()*0.02), # Pequeño offset en Y
        text, 
        fontsize=10, 
        fontweight='bold',
        color='0.1',
        bbox=dict(facecolor='white', alpha=0.5, edgecolor='none', boxstyle='round,pad=0.2') # Fondo suave para el texto
    )

# Estética Profesional
plt.title('Matriz de Trade-off: Latencia RTT vs Rendimiento Global', fontsize=16, pad=20, fontweight='bold')
plt.xlabel('Latencia RTT Promedio (ms) - MENOS ES MEJOR', fontsize=12, labelpad=15)
plt.ylabel('Rendimiento Promedio (img/s) - MÁS ES MEJOR', fontsize=12, labelpad=15)

# Formatear eje Y con 'K'
ax3.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f'{x/1000:.0f}K'))

# Añadir rejilla sutil extra para ver mejor los valores
ax3.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)

# Ocultar la leyenda ya que hemos etiquetado los puntos directamente (diseño más limpio)
plt.gca().get_legend().remove()

plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/graph_3_scatter_tradeoff.png", dpi=300)
plt.close()

# ==============================================================================
# 5. FINALIZACIÓN
# ==============================================================================
print(f"\n¡Éxito absoluto! Tus {len(os.listdir(OUTPUT_DIR))} gráficos profesionales se han guardado en: {OUTPUT_DIR}")
print("   Listos para copiar y pegar en tu memoria final.")