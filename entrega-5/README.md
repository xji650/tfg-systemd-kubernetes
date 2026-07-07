# Comparativa Final: Systemd vs Kubernetes (K3s)

Este directorio conforma la fase de evaluación final del proyecto. Tras determinar que la combinación de **ZeroMQ y MessagePack** es el protocolo de comunicación óptimo para infraestructuras Edge, esta sección enfrenta los dos paradigmas de orquestación evaluados a lo largo del estudio: la ejecución nativa y local (Systemd) contra la orquestación distribuida y virtualizada (Kubernetes).

El objetivo de esta estructura es unificar los *Data Lakes* de ambas arquitecturas para extraer el "Impuesto Arquitectónico" (overhead) real que supone desplegar un clúster de Kubernetes en dispositivos perimetrales limitados.

## Estructura del Directorio

* `resultados_systemd.csv`: Conjunto de datos base que contiene las métricas históricas extraídas durante las pruebas de la arquitectura nativa.

* `resultados_k3s.csv`: Conjunto de datos base con las métricas de la arquitectura basada en Kubernetes.

* `generar_comparativa.py`: Script analítico en Python diseñado para cruzar ambos conjuntos de datos, aislar el protocolo ganador y generar visualizaciones directas de rendimiento.

* `visualizations_final/`: Directorio autogenerado que contiene las gráficas de la comparativa (consumo de RAM, resiliencia MTTR y Throughput).

* `05-conclusion-final.md`: Documento académico que interpreta los resultados visuales, justifica el tratamiento estadístico aplicado a los datos (*Data Cleansing*) y presenta el veredicto arquitectónico del proyecto.

* `README.md`: Este documento descriptivo.

## Ejecución de la Comparativa

Para regenerar las gráficas cruzadas a partir de los archivos CSV provistos, ejecuta el script principal asegurándote de tener instaladas las librerías de visualización:

```bash
# 1. Instalar dependencias requeridas
pip install pandas matplotlib seaborn

# 2. Ejecutar la fusión de datos y renderizado de gráficas
python3 generar_comparativa.py