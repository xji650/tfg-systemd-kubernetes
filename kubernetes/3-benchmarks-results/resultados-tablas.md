# Resultados Consolidados del Proyecto
> **Nota:** Estas tablas representan la **media histórica total** de todas las ejecuciones almacenadas en el Data Lake (`resultados-globales.csv`).

## Protocolo: 01-http-json (Basado en 5 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 104.84 s |
| **Recuperación (MTTR)** | 1672.64 ms |
| **CPU Reposo** | 1.10 % |
| **RAM Reposo** | 851.10 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.99 s |
| **Throughput** | 2086.61 img/s |
| **Latencia RTT** | 516.90 ms |
| **T_Proc Worker** | 503.45 ms |
| **RAM Máxima** | 337.30 MB |
| **CPU Máxima** | 138.94 % |
| **Payload Red** | 15.59 MB |

---

## Protocolo: 02-grpc-protobuf (Basado en 5 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 131.58 s |
| **Recuperación (MTTR)** | 1571.98 ms |
| **CPU Reposo** | 1.00 % |
| **RAM Reposo** | 849.00 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.33 s |
| **Throughput** | 6358.87 img/s |
| **Latencia RTT** | 319.32 ms |
| **T_Proc Worker** | 281.93 ms |
| **RAM Máxima** | 392.79 MB |
| **CPU Máxima** | 186.82 % |
| **Payload Red** | 2.99 MB |

---

## Protocolo: 03-zeromq-protobuf (Basado en 5 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 96.06 s |
| **Recuperación (MTTR)** | 1643.34 ms |
| **CPU Reposo** | 1.30 % |
| **RAM Reposo** | 852.50 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.31 s |
| **Throughput** | 7033.38 img/s |
| **Latencia RTT** | 263.85 ms |
| **T_Proc Worker** | 201.72 ms |
| **RAM Máxima** | 282.18 MB |
| **CPU Máxima** | 194.28 % |
| **Payload Red** | 2.99 MB |

---

## Protocolo: 04-zeromq-messagepack (Basado en 5 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 137.91 s |
| **Recuperación (MTTR)** | 1472.56 ms |
| **CPU Reposo** | 0.80 % |
| **RAM Reposo** | 852.00 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.33 s |
| **Throughput** | 6555.69 img/s |
| **Latencia RTT** | 277.54 ms |
| **T_Proc Worker** | 203.35 ms |
| **RAM Máxima** | 275.12 MB |
| **CPU Máxima** | 196.35 % |
| **Payload Red** | 2.99 MB |

---

