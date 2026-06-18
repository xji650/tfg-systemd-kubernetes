# Resultados Consolidados del Proyecto
> **Nota:** Estas tablas representan la **media histórica total** de todas las ejecuciones almacenadas en el Data Lake (`resultados_globales.csv`).

## Protocolo: 01-http-json (Basado en 2 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 19.70 s |
| **Recuperación (MTTR)** | 818.02 ms |
| **CPU Reposo** | 5.05 % |
| **RAM Reposo** | 32.26 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 16.52 s |
| **Throughput** | 3636.87 img/s |
| **Latencia RTT** | 10800.24 ms |
| **T_Proc Worker** | 10693.67 ms |
| **RAM Máxima** | 2597.53 MB |
| **CPU Máxima** | 99.28 % |
| **Payload Red** | 121.14 MB |

---

## Protocolo: 02-grpc-protobuf (Basado en 2 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 34.35 s |
| **Recuperación (MTTR)** | 919.15 ms |
| **CPU Reposo** | 5.18 % |
| **RAM Reposo** | 23.85 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 1.04 s |
| **Throughput** | 57850.51 img/s |
| **Latencia RTT** | 1023.90 ms |
| **T_Proc Worker** | 127.79 ms |
| **RAM Máxima** | 384.82 MB |
| **CPU Máxima** | 98.97 % |
| **Payload Red** | 89.72 MB |

---

## Protocolo: 03-zeromq-protobuf (Basado en 2 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 25.32 s |
| **Recuperación (MTTR)** | 849.81 ms |
| **CPU Reposo** | 3.75 % |
| **RAM Reposo** | 17.60 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.68 s |
| **Throughput** | 88430.12 img/s |
| **Latencia RTT** | 672.39 ms |
| **T_Proc Worker** | 266.94 ms |
| **RAM Máxima** | 301.05 MB |
| **CPU Máxima** | 98.52 % |
| **Payload Red** | 89.72 MB |

---

## Protocolo: 04-zeromq-messagepack (Basado en 2 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 29.83 s |
| **Recuperación (MTTR)** | 869.89 ms |
| **CPU Reposo** | 3.17 % |
| **RAM Reposo** | 16.14 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.54 s |
| **Throughput** | 111087.53 img/s |
| **Latencia RTT** | 529.74 ms |
| **T_Proc Worker** | 124.75 ms |
| **RAM Máxima** | 209.26 MB |
| **CPU Máxima** | 97.78 % |
| **Payload Red** | 89.72 MB |

---

