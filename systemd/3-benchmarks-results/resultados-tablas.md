# Resultados Consolidados del Proyecto
> **Nota:** Estas tablas representan la **media histórica total** de todas las ejecuciones almacenadas en el Data Lake (`resultados-globales.csv`).

## Protocolo: 01-http-json (Basado en 10 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 198.35 s |
| **Recuperación (MTTR)** | 464.89 ms |
| **CPU Reposo** | 0.05 % |
| **RAM Reposo** | 727.95 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.82 s |
| **Throughput** | 2451.78 img/s |
| **Latencia RTT** | 429.27 ms |
| **T_Proc Worker** | 415.03 ms |
| **RAM Máxima** | 328.96 MB |
| **CPU Máxima** | 141.17 % |
| **Payload Red** | 15.59 MB |

---

## Protocolo: 02-grpc-protobuf (Basado en 10 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 181.51 s |
| **Recuperación (MTTR)** | 455.96 ms |
| **CPU Reposo** | 0.25 % |
| **RAM Reposo** | 729.60 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.23 s |
| **Throughput** | 8594.21 img/s |
| **Latencia RTT** | 223.89 ms |
| **T_Proc Worker** | 200.66 ms |
| **RAM Máxima** | 309.52 MB |
| **CPU Máxima** | 196.66 % |
| **Payload Red** | 2.99 MB |

---

## Protocolo: 03-zeromq-protobuf (Basado en 10 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 111.39 s |
| **Recuperación (MTTR)** | 452.10 ms |
| **CPU Reposo** | 0.10 % |
| **RAM Reposo** | 720.10 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.22 s |
| **Throughput** | 9092.66 img/s |
| **Latencia RTT** | 216.63 ms |
| **T_Proc Worker** | 202.14 ms |
| **RAM Máxima** | 277.22 MB |
| **CPU Máxima** | 195.47 % |
| **Payload Red** | 2.99 MB |

---

## Protocolo: 04-zeromq-messagepack (Basado en 10 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 218.67 s |
| **Recuperación (MTTR)** | 452.09 ms |
| **CPU Reposo** | 0.00 % |
| **RAM Reposo** | 722.50 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.22 s |
| **Throughput** | 9053.76 img/s |
| **Latencia RTT** | 215.61 ms |
| **T_Proc Worker** | 199.55 ms |
| **RAM Máxima** | 284.26 MB |
| **CPU Máxima** | 196.59 % |
| **Payload Red** | 2.99 MB |

---

