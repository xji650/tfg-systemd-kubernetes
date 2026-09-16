# Resultados Consolidados del Proyecto
> **Nota:** Estas tablas representan la **media histórica total** de todas las ejecuciones almacenadas en el Data Lake (`resultados-globales.csv`).

## Protocolo: 01-http-json (Basado en 10 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 122.61 s |
| **Recuperación (MTTR)** | 1606.99 ms |
| **CPU Reposo** | 0.85 % |
| **RAM Reposo** | 829.25 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 1.02 s |
| **Throughput** | 2015.11 img/s |
| **Latencia RTT** | 538.51 ms |
| **T_Proc Worker** | 525.76 ms |
| **RAM Máxima** | 344.65 MB |
| **CPU Máxima** | 137.55 % |
| **Payload Red** | 15.59 MB |

---

## Protocolo: 02-grpc-protobuf (Basado en 10 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 135.09 s |
| **Recuperación (MTTR)** | 26688.57 ms |
| **CPU Reposo** | 0.80 % |
| **RAM Reposo** | 819.65 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.34 s |
| **Throughput** | 6356.45 img/s |
| **Latencia RTT** | 323.57 ms |
| **T_Proc Worker** | 289.91 ms |
| **RAM Máxima** | 370.06 MB |
| **CPU Máxima** | 178.39 % |
| **Payload Red** | 2.99 MB |

---

## Protocolo: 03-zeromq-protobuf (Basado en 10 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 90.60 s |
| **Recuperación (MTTR)** | 1604.90 ms |
| **CPU Reposo** | 1.00 % |
| **RAM Reposo** | 840.60 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.33 s |
| **Throughput** | 6660.90 img/s |
| **Latencia RTT** | 278.48 ms |
| **T_Proc Worker** | 216.09 ms |
| **RAM Máxima** | 284.07 MB |
| **CPU Máxima** | 190.23 % |
| **Payload Red** | 2.99 MB |

---

## Protocolo: 04-zeromq-messagepack (Basado en 10 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 145.16 s |
| **Recuperación (MTTR)** | 1485.81 ms |
| **CPU Reposo** | 0.80 % |
| **RAM Reposo** | 834.40 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.34 s |
| **Throughput** | 6269.21 img/s |
| **Latencia RTT** | 284.99 ms |
| **T_Proc Worker** | 205.62 ms |
| **RAM Máxima** | 280.90 MB |
| **CPU Máxima** | 193.83 % |
| **Payload Red** | 2.99 MB |

---

