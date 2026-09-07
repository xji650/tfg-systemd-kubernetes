# Resultados Consolidados del Proyecto
> **Nota:** Estas tablas representan la **media histórica total** de todas las ejecuciones almacenadas en el Data Lake (`resultados-globales.csv`).

## Protocolo: 01-http-json (Basado en 6 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 121.34 s |
| **Recuperación (MTTR)** | 1602.39 ms |
| **CPU Reposo** | 1.08 % |
| **RAM Reposo** | 845.42 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 1.00 s |
| **Throughput** | 2069.86 img/s |
| **Latencia RTT** | 523.17 ms |
| **T_Proc Worker** | 509.95 ms |
| **RAM Máxima** | 342.80 MB |
| **CPU Máxima** | 138.17 % |
| **Payload Red** | 15.59 MB |

---

## Protocolo: 02-grpc-protobuf (Basado en 6 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 143.68 s |
| **Recuperación (MTTR)** | 43529.97 ms |
| **CPU Reposo** | 0.92 % |
| **RAM Reposo** | 829.33 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.33 s |
| **Throughput** | 6375.82 img/s |
| **Latencia RTT** | 318.36 ms |
| **T_Proc Worker** | 282.04 ms |
| **RAM Máxima** | 387.57 MB |
| **CPU Máxima** | 189.11 % |
| **Payload Red** | 2.99 MB |

---

## Protocolo: 03-zeromq-protobuf (Basado en 6 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 93.31 s |
| **Recuperación (MTTR)** | 1548.16 ms |
| **CPU Reposo** | 1.17 % |
| **RAM Reposo** | 850.67 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.31 s |
| **Throughput** | 6940.48 img/s |
| **Latencia RTT** | 265.65 ms |
| **T_Proc Worker** | 202.92 ms |
| **RAM Máxima** | 281.59 MB |
| **CPU Máxima** | 193.86 % |
| **Payload Red** | 2.99 MB |

---

## Protocolo: 04-zeromq-messagepack (Basado en 6 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 152.02 s |
| **Recuperación (MTTR)** | 1561.26 ms |
| **CPU Reposo** | 0.75 % |
| **RAM Reposo** | 846.00 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.34 s |
| **Throughput** | 6435.78 img/s |
| **Latencia RTT** | 280.00 ms |
| **T_Proc Worker** | 204.46 ms |
| **RAM Máxima** | 276.63 MB |
| **CPU Máxima** | 195.38 % |
| **Payload Red** | 2.99 MB |

---

