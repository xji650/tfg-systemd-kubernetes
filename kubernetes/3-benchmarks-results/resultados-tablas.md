# Resultados Consolidados del Proyecto
> **Nota:** Estas tablas representan la **media histórica total** de todas las ejecuciones almacenadas en el Data Lake (`resultados-globales.csv`).

## Protocolo: 01-http-json (Basado en 9 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 121.28 s |
| **Recuperación (MTTR)** | 1586.11 ms |
| **CPU Reposo** | 0.89 % |
| **RAM Reposo** | 832.11 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.66 s |
| **Throughput** | 1379.90 img/s |
| **Latencia RTT** | 348.78 ms |
| **T_Proc Worker** | 339.97 ms |
| **RAM Máxima** | 228.53 MB |
| **CPU Máxima** | 92.12 % |
| **Payload Red** | 10.39 MB |

---

## Protocolo: 02-grpc-protobuf (Basado en 9 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 141.52 s |
| **Recuperación (MTTR)** | 29532.10 ms |
| **CPU Reposo** | 0.67 % |
| **RAM Reposo** | 822.61 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.22 s |
| **Throughput** | 4250.55 img/s |
| **Latencia RTT** | 212.24 ms |
| **T_Proc Worker** | 188.02 ms |
| **RAM Máxima** | 258.38 MB |
| **CPU Máxima** | 126.07 % |
| **Payload Red** | 1.99 MB |

---

## Protocolo: 03-zeromq-protobuf (Basado en 9 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 96.01 s |
| **Recuperación (MTTR)** | 1523.04 ms |
| **CPU Reposo** | 0.83 % |
| **RAM Reposo** | 841.06 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.21 s |
| **Throughput** | 4626.99 img/s |
| **Latencia RTT** | 177.10 ms |
| **T_Proc Worker** | 135.28 ms |
| **RAM Máxima** | 187.72 MB |
| **CPU Máxima** | 129.24 % |
| **Payload Red** | 1.99 MB |

---

## Protocolo: 04-zeromq-messagepack (Basado en 9 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 145.62 s |
| **Recuperación (MTTR)** | 1574.13 ms |
| **CPU Reposo** | 0.67 % |
| **RAM Reposo** | 835.28 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.22 s |
| **Throughput** | 4290.52 img/s |
| **Latencia RTT** | 186.66 ms |
| **T_Proc Worker** | 136.31 ms |
| **RAM Máxima** | 184.42 MB |
| **CPU Máxima** | 130.26 % |
| **Payload Red** | 1.99 MB |

---

