# Resultados Consolidados del Proyecto
> **Nota:** Estas tablas representan la **media histórica total** de todas las ejecuciones almacenadas en el Data Lake (`resultados-globales.csv`).

## Protocolo: 01-http-json (Basado en 3 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 246.79 s |
| **Recuperación (MTTR)** | 760.26 ms |
| **CPU Reposo** | 24.94 % |
| **RAM Reposo** | 169.02 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 1.13 s |
| **Throughput** | 1845.01 img/s |
| **Latencia RTT** | 722.69 ms |
| **T_Proc Worker** | 704.29 ms |
| **RAM Máxima** | 335.23 MB |
| **CPU Máxima** | 152.57 % |
| **Payload Red** | 15.59 MB |

---

## Protocolo: 02-grpc-protobuf (Basado en 3 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 249.14 s |
| **Recuperación (MTTR)** | 798.78 ms |
| **CPU Reposo** | 20.96 % |
| **RAM Reposo** | 156.50 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.48 s |
| **Throughput** | 4923.26 img/s |
| **Latencia RTT** | 467.50 ms |
| **T_Proc Worker** | 433.12 ms |
| **RAM Máxima** | 311.71 MB |
| **CPU Máxima** | 193.96 % |
| **Payload Red** | 2.99 MB |

---

## Protocolo: 03-zeromq-protobuf (Basado en 3 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 214.67 s |
| **Recuperación (MTTR)** | 808.86 ms |
| **CPU Reposo** | 19.96 % |
| **RAM Reposo** | 154.20 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.46 s |
| **Throughput** | 5300.36 img/s |
| **Latencia RTT** | 458.74 ms |
| **T_Proc Worker** | 437.63 ms |
| **RAM Máxima** | 279.49 MB |
| **CPU Máxima** | 194.88 % |
| **Payload Red** | 2.99 MB |

---

## Protocolo: 04-zeromq-messagepack (Basado en 3 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 254.99 s |
| **Recuperación (MTTR)** | 773.29 ms |
| **CPU Reposo** | 20.09 % |
| **RAM Reposo** | 152.80 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.48 s |
| **Throughput** | 5127.61 img/s |
| **Latencia RTT** | 470.81 ms |
| **T_Proc Worker** | 449.49 ms |
| **RAM Máxima** | 269.69 MB |
| **CPU Máxima** | 194.91 % |
| **Payload Red** | 2.99 MB |

---

