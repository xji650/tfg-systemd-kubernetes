# Resultados Consolidados del Proyecto
> **Nota:** Estas tablas representan la **media histórica total** de todas las ejecuciones almacenadas en el Data Lake (`resultados_globales.csv`).

## Protocolo: 01-http-json (Basado en 2 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 281.49 s |
| **Recuperación (MTTR)** | 897.85 ms |
| **CPU Reposo** | 28.22 % |
| **RAM Reposo** | 169.03 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 1.27 s |
| **Throughput** | 1585.65 img/s |
| **Latencia RTT** | 865.18 ms |
| **T_Proc Worker** | 845.82 ms |
| **RAM Máxima** | 338.16 MB |
| **CPU Máxima** | 158.31 % |
| **Payload Red** | 15.59 MB |

---

## Protocolo: 02-grpc-protobuf (Basado en 2 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 288.09 s |
| **Recuperación (MTTR)** | 915.43 ms |
| **CPU Reposo** | 22.61 % |
| **RAM Reposo** | 156.50 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.60 s |
| **Throughput** | 3337.02 img/s |
| **Latencia RTT** | 585.35 ms |
| **T_Proc Worker** | 547.83 ms |
| **RAM Máxima** | 311.65 MB |
| **CPU Máxima** | 194.64 % |
| **Payload Red** | 2.99 MB |

---

## Protocolo: 03-zeromq-protobuf (Basado en 2 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 234.45 s |
| **Recuperación (MTTR)** | 938.76 ms |
| **CPU Reposo** | 22.64 % |
| **RAM Reposo** | 154.20 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.58 s |
| **Throughput** | 3422.66 img/s |
| **Latencia RTT** | 579.32 ms |
| **T_Proc Worker** | 555.89 ms |
| **RAM Máxima** | 281.59 MB |
| **CPU Máxima** | 192.90 % |
| **Payload Red** | 2.99 MB |

---

## Protocolo: 04-zeromq-messagepack (Basado en 2 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 286.19 s |
| **Recuperación (MTTR)** | 918.56 ms |
| **CPU Reposo** | 22.48 % |
| **RAM Reposo** | 152.80 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.60 s |
| **Throughput** | 3331.24 img/s |
| **Latencia RTT** | 593.12 ms |
| **T_Proc Worker** | 569.30 ms |
| **RAM Máxima** | 269.63 MB |
| **CPU Máxima** | 193.73 % |
| **Payload Red** | 2.99 MB |

---

