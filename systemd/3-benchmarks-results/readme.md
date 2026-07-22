# Benchmarks Results

Esta carpeta contiene la infraestructura de datos y el análisis técnico consolidado de la comparativa de protocolos (HTTP, gRPC, ZeroMQ) realizada sobre el clúster Edge.

## Estructura del Directorio
* `raw_logs/`: Directorio raíz de los archivos `.log` crudos generados por el clúster durante los experimentos.
* `visualizations/`: Gráficas comparativas resultantes del análisis de rendimiento generadas por `generate_graphs.py`.
* `calculate_benchmarks_avg.py`: Script de procesamiento que calcula las medias históricas y genera el archivo de tablas `resultados_tablas.md`.
* `generate_graphs.py`: Script que genera las gráficas de rendimiento y son guardados en `visualizations/`.
* `resultados_globales.csv`: Dataset consolidado tras procesar los logs.
* `resultados_tablas.md`: Reporte generado por `calculate_benchmarks_avg.py` con las tablas de métricas en formato Markdown.
* `benchmarks-analisis.md`: Informe de analisis y comparativa de métricas de los diferentes protocolos con su correspondiente seriarización.
* `readme.md`: Información general este directorio.



## Ejecución del Análisis
Para regenerar los resultados a partir de los logs crudos, ejecuta:
```bash
python3 calculate_benchmarks_avg.py
python3 generate_graphs.py
```
---

