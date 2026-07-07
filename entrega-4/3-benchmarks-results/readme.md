# Resultados y Análisis de Benchmarking

Este directorio contiene los datos estructurados, los scripts de procesamiento y el análisis técnico de la comparativa de protocolos de red desplegados sobre el clúster Edge de **Kubernetes (K3s)**.

Los datos almacenados recogen la evaluación de rendimiento bajo estrés de cuatro implementaciones arquitectónicas:
1. HTTP/1.1 con JSON
2. gRPC con Protocol Buffers
3. ZeroMQ (TCP) con Protocol Buffers
4. ZeroMQ (TCP) con MessagePack

## Estructura del Directorio

* `raw_logs/`: Contiene los archivos `.log` crudos generados por los scripts de automatización durante las pruebas de carga.

* `visualizations/`: Directorio de salida para las gráficas comparativas de rendimiento generadas a partir del histórico de datos.

* `calculate_benchmarks_avg.py`: Script de procesamiento que lee el archivo CSV, calcula las medias históricas y genera el documento Markdown de resultados.

* `generate_graphs.py`: Script de visualización que transforma el dataset en gráficas utilizando las librerías `pandas` y `seaborn`.

* `resultados_globales.csv`: Dataset consolidado. Almacena las métricas de red y el consumo de infraestructura (CPU y RAM a nivel de Sistema Operativo).

* `resultados-tablas.md`: Documento autogenerado con las tablas de métricas agregadas por protocolo.

* `benchmarks-analisis.md`: Informe técnico que interpreta las métricas, justifica la metodología de medición y expone las conclusiones de la comparativa.

* `README.md`: Este documento de referencia y guía de uso.

## Ejecución del Análisis

Para recalcular las medias y regenerar las visualizaciones tras registrar nuevos datos en el archivo `resultados_globales.csv`, se deben ejecutar los siguientes comandos:

```bash
# 1. Instalar dependencias de procesamiento de datos (si no están presentes)
pip install pandas matplotlib seaborn

# 2. Generar el reporte de tablas actualizadas (resultados-tablas.md)
python3 calculate_benchmarks_avg.py

# 3. Renderizar las gráficas comparativas en el directorio /visualizations
python3 generate_graphs.py
```
---