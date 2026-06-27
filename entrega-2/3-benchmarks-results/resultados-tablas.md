# Resultados Consolidados del Proyecto
> **Nota:** Estas tablas representan la **media histórica total** de todas las ejecuciones almacenadas en el Data Lake (`resultados_globales.csv`).

## Protocolo: 01-http-json (Basado en 4 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 23.21 s |
| **Recuperación (MTTR)** | 849.02 ms |
| **CPU Reposo** | 5.48 % |
| **RAM Reposo** | 32.41 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 17.52 s |
| **Throughput** | 3454.38 img/s |
| **Latencia RTT** | 11641.24 ms |
| **T_Proc Worker** | 11414.16 ms |
| **RAM Máxima** | 2599.45 MB |
| **CPU Máxima** | 99.23 % |
| **Payload Red** | 121.14 MB |

---

## Protocolo: 02-grpc-protobuf (Basado en 4 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 34.44 s |
| **Recuperación (MTTR)** | 897.96 ms |
| **CPU Reposo** | 5.44 % |
| **RAM Reposo** | 23.86 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 1.10 s |
| **Throughput** | 54615.17 img/s |
| **Latencia RTT** | 1082.71 ms |
| **T_Proc Worker** | 129.40 ms |
| **RAM Máxima** | 361.79 MB |
| **CPU Máxima** | 99.69 % |
| **Payload Red** | 89.72 MB |

---

## Protocolo: 03-zeromq-protobuf (Basado en 4 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 29.97 s |
| **Recuperación (MTTR)** | 865.20 ms |
| **CPU Reposo** | 3.64 % |
| **RAM Reposo** | 17.31 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.70 s |
| **Throughput** | 85707.36 img/s |
| **Latencia RTT** | 689.52 ms |
| **T_Proc Worker** | 270.59 ms |
| **RAM Máxima** | 300.65 MB |
| **CPU Máxima** | 98.77 % |
| **Payload Red** | 89.72 MB |

---

## Protocolo: 04-zeromq-messagepack (Basado en 4 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 29.45 s |
| **Recuperación (MTTR)** | 878.76 ms |
| **CPU Reposo** | 3.38 % |
| **RAM Reposo** | 15.86 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.55 s |
| **Throughput** | 108436.14 img/s |
| **Latencia RTT** | 543.88 ms |
| **T_Proc Worker** | 127.72 ms |
| **RAM Máxima** | 209.11 MB |
| **CPU Máxima** | 98.05 % |
| **Payload Red** | 89.72 MB |

---

