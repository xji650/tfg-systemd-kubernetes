# RESULTADOS BENCHMARK DE INFRAESTRUCTURA

## Test 1

```
=========================================================
 INICIANDO BENCHMARK AUTOMATIZADO DE INFRAESTRUCTURA
=========================================================
[1/4] Lanzando Ansible y cronometrando T_deploy para todos los nodos...
  ...
  [OK] T_deploy total (Clúster): 25.31 segundos

---------------------------------------------------------
 EVALUANDO NODO: 192.168.98.143
---------------------------------------------------------
[2/4] Midiendo RAM y CPU en reposo...
  [OK] CPU Reposo: 6.51% | RAM Reposo: 32.51MB / 4.056GB
[3/4 y 4/4] Simulación de fallo y cronometrando recuperación...
  -> Forzando caída del contenedor (Chaos Testing)...
  [OK] Tiempo Real de Arranque: 465.62 ms (Tiempo Total MTTR: 3465.62 ms)

---------------------------------------------------------
 EVALUANDO NODO: 192.168.98.144
---------------------------------------------------------
[2/4] Midiendo RAM y CPU en reposo...
  [OK] CPU Reposo: 3.02% | RAM Reposo: 32.51MB / 4.056GB
[3/4 y 4/4] Simulación de fallo y cronometrando recuperación...
  -> Forzando caída del contenedor (Chaos Testing)...
  [OK] Tiempo Real de Arranque: 472.84 ms (Tiempo Total MTTR: 3472.84 ms)

=========================================================
 BENCHMARK MULTINODO FINALIZADO
=========================================================
```

## Test 2

```
=========================================================
 INICIANDO BENCHMARK AUTOMATIZADO DE INFRAESTRUCTURA
=========================================================
[1/4] Lanzando Ansible y cronometrando T_deploy para todos los nodos...
  ...
  [OK] T_deploy total (Clúster): 26.2 segundos

---------------------------------------------------------
 EVALUANDO NODO: 192.168.98.143
---------------------------------------------------------
[2/4] Midiendo RAM y CPU en reposo...
  [OK] CPU Reposo: 6.31% | RAM Reposo: 32.51MB / 4.056GB
[3/4 y 4/4] Simulación de fallo y cronometrando recuperación...
  -> Forzando caída del contenedor (Chaos Testing)...
  [OK] Tiempo Real de Arranque: 465.85 ms (Tiempo Total MTTR: 3465.85 ms)

---------------------------------------------------------
 EVALUANDO NODO: 192.168.98.144
---------------------------------------------------------
[2/4] Midiendo RAM y CPU en reposo...
  [OK] CPU Reposo: 3.07% | RAM Reposo: 32.51MB / 4.056GB
[3/4 y 4/4] Simulación de fallo y cronometrando recuperación...
  -> Forzando caída del contenedor (Chaos Testing)...
  [OK] Tiempo Real de Arranque: 491.28 ms (Tiempo Total MTTR: 3491.28 ms)

=========================================================
 BENCHMARK MULTINODO FINALIZADO
=========================================================
```

## Test 3

```
=========================================================
 INICIANDO BENCHMARK AUTOMATIZADO DE INFRAESTRUCTURA
=========================================================
[1/4] Lanzando Ansible y cronometrando T_deploy para todos los nodos...
  ...
  [OK] T_deploy total (Clúster): 26.61 segundos

---------------------------------------------------------
 EVALUANDO NODO: 192.168.98.143
---------------------------------------------------------
[2/4] Midiendo RAM y CPU en reposo...
  [OK] CPU Reposo: 6.31% | RAM Reposo: 32.51MB / 4.056GB
[3/4 y 4/4] Simulación de fallo y cronometrando recuperación...
  -> Forzando caída del contenedor (Chaos Testing)...
  [OK] Tiempo Real de Arranque: 440.5 ms (Tiempo Total MTTR: 3440.5 ms)

---------------------------------------------------------
 EVALUANDO NODO: 192.168.98.144
---------------------------------------------------------
[2/4] Midiendo RAM y CPU en reposo...
  [OK] CPU Reposo: 3.09% | RAM Reposo: 32.51MB / 4.056GB
[3/4 y 4/4] Simulación de fallo y cronometrando recuperación...
  -> Forzando caída del contenedor (Chaos Testing)...
  [OK] Tiempo Real de Arranque: 466.77 ms (Tiempo Total MTTR: 3466.77 ms)

=========================================================
 BENCHMARK MULTINODO FINALIZADO
=========================================================
```

## Test 4

```
=========================================================
 INICIANDO BENCHMARK AUTOMATIZADO DE INFRAESTRUCTURA
=========================================================
[1/4] Lanzando Ansible y cronometrando T_deploy para todos los nodos...
  ...
  [OK] T_deploy total (Clúster): 31.12 segundos

---------------------------------------------------------
 EVALUANDO NODO: 192.168.98.143
---------------------------------------------------------
[2/4] Midiendo RAM y CPU en reposo...
  [OK] CPU Reposo: 6.23% | RAM Reposo: 32.51MB / 4.056GB
[3/4 y 4/4] Simulación de fallo y cronometrando recuperación...
  -> Forzando caída del contenedor (Chaos Testing)...
  [OK] Tiempo Real de Arranque: 500.85 ms (Tiempo Total MTTR: 3500.85 ms)

---------------------------------------------------------
 EVALUANDO NODO: 192.168.98.144
---------------------------------------------------------
[2/4] Midiendo RAM y CPU en reposo...
  [OK] CPU Reposo: 3.23% | RAM Reposo: 32.51MB / 4.056GB
[3/4 y 4/4] Simulación de fallo y cronometrando recuperación...
  -> Forzando caída del contenedor (Chaos Testing)...
  [OK] Tiempo Real de Arranque: 450.25 ms (Tiempo Total MTTR: 3450.25 ms)

=========================================================
 BENCHMARK MULTINODO FINALIZADO
=========================================================
```

## Test 5

```
=========================================================
 INICIANDO BENCHMARK AUTOMATIZADO DE INFRAESTRUCTURA
=========================================================
[1/4] Lanzando Ansible y cronometrando T_deploy para todos los nodos...
  ...
  [OK] T_deploy total (Clúster): 25.9 segundos

---------------------------------------------------------
 EVALUANDO NODO: 192.168.98.143
---------------------------------------------------------
[2/4] Midiendo RAM y CPU en reposo...
  [OK] CPU Reposo: 6.17% | RAM Reposo: 32.52MB / 4.056GB
[3/4 y 4/4] Simulación de fallo y cronometrando recuperación...
  -> Forzando caída del contenedor (Chaos Testing)...
  [OK] Tiempo Real de Arranque: 440.49 ms (Tiempo Total MTTR: 3440.49 ms)

---------------------------------------------------------
 EVALUANDO NODO: 192.168.98.144
---------------------------------------------------------
[2/4] Midiendo RAM y CPU en reposo...
  [OK] CPU Reposo: 3.19% | RAM Reposo: 32.52MB / 4.056GB
[3/4 y 4/4] Simulación de fallo y cronometrando recuperación...
  -> Forzando caída del contenedor (Chaos Testing)...
  [OK] Tiempo Real de Arranque: 427.76 ms (Tiempo Total MTTR: 3427.76 ms)

=========================================================
 BENCHMARK MULTINODO FINALIZADO
=========================================================
```

## Tabla 1: Resultados Desglosados por Prueba

| Prueba | T_deploy Clúster | Nodo Evaluado | CPU Reposo | RAM Reposo | T_Arranque Real | MTTR Total |
| --- | --- | --- | --- | --- | --- | --- |
| **Test 1** | 25.31 s | 192.168.98.143 | 6.51 % | 32.51 MB | 465.62 ms | 3465.62 ms |
|  |  | 192.168.98.144 | 3.02 % | 32.51 MB | 472.84 ms | 3472.84 ms |
| **Test 2** | 26.20 s | 192.168.98.143 | 6.31 % | 32.51 MB | 465.85 ms | 3465.85 ms |
|  |  | 192.168.98.144 | 3.07 % | 32.51 MB | 491.28 ms | 3491.28 ms |
| **Test 3** | 26.61 s | 192.168.98.143 | 6.31 % | 32.51 MB | 440.50 ms | 3440.50 ms |
|  |  | 192.168.98.144 | 3.09 % | 32.51 MB | 466.77 ms | 3466.77 ms |
| **Test 4** | 31.12 s | 192.168.98.143 | 6.23 % | 32.51 MB | 500.85 ms | 3500.85 ms |
|  |  | 192.168.98.144 | 3.23 % | 32.51 MB | 450.25 ms | 3450.25 ms |
| **Test 5** | 25.90 s | 192.168.98.143 | 6.17 % | 32.52 MB | 440.49 ms | 3440.49 ms |
|  |  | 192.168.98.144 | 3.19 % | 32.52 MB | 427.76 ms | 3427.76 ms |

---

## Tabla 2: Promedios Consolidados (Para el análisis de tu TFG)

Esta es la tabla que debes usar para demostrar la resiliencia y eficiencia de tu infraestructura en la memoria.

| Métrica de Infraestructura | Nodo 192.168.98.143 | Nodo 192.168.98.144 | **Promedio Global del Clúster** |
| --- | --- | --- | --- |
| **Tiempo Despliegue ($T_{deploy}$)** | - | - | **27.03 s** |
| **CPU en Reposo (Idle)** | 6.31 % | 3.12 % | **4.71 %** |
| **RAM en Reposo (Idle)** | 32.51 MB | 32.51 MB | **32.51 MB** |
| **Tiempo de Arranque Real** | 462.66 ms | 461.78 ms | **462.22 ms** |
| **MTTR Total (con delay 3s)** | 3462.66 ms | 3461.78 ms | **3462.22 ms** |

---

## Análisis Técnico Sugerido para tu Memoria

>Los resultados del benchmark de infraestructura revelan una alta consistencia en el rendimiento del clúster Edge. El tiempo de aprovisionamiento mediante Ansible ($T_{deploy}$) es de **~27 segundos**, permitiendo una escalabilidad horizontal rápida.

> En estado de reposo, los nodos demuestran ser extremadamente eficientes, con una huella de memoria idéntica de **32.51 MB** por contenedor y un consumo de CPU marginal (<5%).

> Finalmente, las pruebas de Chaos Testing validan el mecanismo de Self-Healing. El sistema gestionado por systemd (Quadlets) es capaz de detectar fallos críticos y levantar un nuevo contenedor plenamente operativo en un tiempo real promedio de **462 milisegundos**. El MTTR final de ~3.46 segundos respeta la regla de seguridad de `RestartSec=3` configurada deliberadamente para prevenir tormentas de reinicios.