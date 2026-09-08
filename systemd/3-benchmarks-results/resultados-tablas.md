# Resultados Consolidados del Proyecto
> **Nota:** Estas tablas representan la **media histórica total** de todas las ejecuciones almacenadas en el Data Lake (`resultados-globales.csv`).

## Protocolo: 01-http-json (Basado en 9 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 177.16 s |
| **Recuperación (MTTR)** | 327.68 ms |
| **CPU Reposo** | 0.06 % |
| **RAM Reposo** | 731.44 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.83 s |
| **Throughput** | 2435.74 img/s |
| **Latencia RTT** | 433.50 ms |
| **T_Proc Worker** | 419.04 ms |
| **RAM Máxima** | 329.14 MB |
| **CPU Máxima** | 141.47 % |
| **Payload Red** | 15.59 MB |

---

## Protocolo: 02-grpc-protobuf (Basado en 9 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 182.99 s |
| **Recuperación (MTTR)** | 329.81 ms |
| **CPU Reposo** | 0.28 % |
| **RAM Reposo** | 731.44 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.23 s |
| **Throughput** | 8545.63 img/s |
| **Latencia RTT** | 225.34 ms |
| **T_Proc Worker** | 201.79 ms |
| **RAM Máxima** | 309.77 MB |
| **CPU Máxima** | 196.38 % |
| **Payload Red** | 2.99 MB |

---

## Protocolo: 03-zeromq-protobuf (Basado en 9 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 122.87 s |
| **Recuperación (MTTR)** | 327.91 ms |
| **CPU Reposo** | 0.06 % |
| **RAM Reposo** | 721.06 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.22 s |
| **Throughput** | 9001.31 img/s |
| **Latencia RTT** | 220.29 ms |
| **T_Proc Worker** | 205.81 ms |
| **RAM Máxima** | 283.57 MB |
| **CPU Máxima** | 195.41 % |
| **Payload Red** | 2.99 MB |

---

## Protocolo: 04-zeromq-messagepack (Basado en 9 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 211.35 s |
| **Recuperación (MTTR)** | 322.29 ms |
| **CPU Reposo** | 0.00 % |
| **RAM Reposo** | 724.56 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.22 s |
| **Throughput** | 8977.72 img/s |
| **Latencia RTT** | 217.33 ms |
| **T_Proc Worker** | 201.94 ms |
| **RAM Máxima** | 278.67 MB |
| **CPU Máxima** | 196.41 % |
| **Payload Red** | 2.99 MB |

---

