# Resultados Consolidados del Proyecto
> **Nota:** Estas tablas representan la **media histórica total** de todas las ejecuciones almacenadas en el Data Lake (`resultados-globales.csv`).

## Protocolo: 01-http-json (Basado en 9 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 181.06 s |
| **Recuperación (MTTR)** | 476.02 ms |
| **CPU Reposo** | 0.06 % |
| **RAM Reposo** | 730.61 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.54 s |
| **Throughput** | 1661.81 img/s |
| **Latencia RTT** | 277.63 ms |
| **T_Proc Worker** | 268.00 ms |
| **RAM Máxima** | 219.41 MB |
| **CPU Máxima** | 94.56 % |
| **Payload Red** | 10.39 MB |

---

## Protocolo: 02-grpc-protobuf (Basado en 9 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 179.62 s |
| **Recuperación (MTTR)** | 475.08 ms |
| **CPU Reposo** | 0.33 % |
| **RAM Reposo** | 729.33 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.16 s |
| **Throughput** | 5747.52 img/s |
| **Latencia RTT** | 149.08 ms |
| **T_Proc Worker** | 132.42 ms |
| **RAM Máxima** | 207.74 MB |
| **CPU Máxima** | 131.47 % |
| **Payload Red** | 1.99 MB |

---

## Protocolo: 03-zeromq-protobuf (Basado en 9 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 124.54 s |
| **Recuperación (MTTR)** | 479.03 ms |
| **CPU Reposo** | 0.06 % |
| **RAM Reposo** | 720.39 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.14 s |
| **Throughput** | 6199.34 img/s |
| **Latencia RTT** | 141.70 ms |
| **T_Proc Worker** | 131.86 ms |
| **RAM Máxima** | 183.74 MB |
| **CPU Máxima** | 131.40 % |
| **Payload Red** | 1.99 MB |

---

## Protocolo: 04-zeromq-messagepack (Basado en 9 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 198.19 s |
| **Recuperación (MTTR)** | 468.27 ms |
| **CPU Reposo** | 0.00 % |
| **RAM Reposo** | 722.72 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.15 s |
| **Throughput** | 6052.72 img/s |
| **Latencia RTT** | 143.14 ms |
| **T_Proc Worker** | 132.39 ms |
| **RAM Máxima** | 186.86 MB |
| **CPU Máxima** | 130.92 % |
| **Payload Red** | 1.99 MB |

---

