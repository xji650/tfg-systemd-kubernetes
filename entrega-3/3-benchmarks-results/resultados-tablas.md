# Resultados Consolidados del Proyecto
> **Nota:** Estas tablas representan la **media histórica total** de todas las ejecuciones almacenadas en el Data Lake (`resultados-globales.csv`).

## Protocolo: 01-http-json (Basado en 5 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 188.01 s |
| **Recuperación (MTTR)** | 495.75 ms |
| **CPU Reposo** | 0.10 % |
| **RAM Reposo** | 734.80 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.80 s |
| **Throughput** | 2490.88 img/s |
| **Latencia RTT** | 415.02 ms |
| **T_Proc Worker** | 400.53 ms |
| **RAM Máxima** | 329.22 MB |
| **CPU Máxima** | 141.60 % |
| **Payload Red** | 15.59 MB |

---

## Protocolo: 02-grpc-protobuf (Basado en 5 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 184.98 s |
| **Recuperación (MTTR)** | 494.53 ms |
| **CPU Reposo** | 0.40 % |
| **RAM Reposo** | 737.10 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.23 s |
| **Throughput** | 8608.73 img/s |
| **Latencia RTT** | 223.53 ms |
| **T_Proc Worker** | 198.25 ms |
| **RAM Máxima** | 312.71 MB |
| **CPU Máxima** | 197.47 % |
| **Payload Red** | 2.99 MB |

---

## Protocolo: 03-zeromq-protobuf (Basado en 5 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 110.94 s |
| **Recuperación (MTTR)** | 482.87 ms |
| **CPU Reposo** | 0.10 % |
| **RAM Reposo** | 720.10 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.22 s |
| **Throughput** | 9333.03 img/s |
| **Latencia RTT** | 211.57 ms |
| **T_Proc Worker** | 196.87 ms |
| **RAM Máxima** | 274.83 MB |
| **CPU Máxima** | 198.20 % |
| **Payload Red** | 2.99 MB |

---

## Protocolo: 04-zeromq-messagepack (Basado en 5 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 199.18 s |
| **Recuperación (MTTR)** | 491.46 ms |
| **CPU Reposo** | 0.00 % |
| **RAM Reposo** | 731.00 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.22 s |
| **Throughput** | 9087.91 img/s |
| **Latencia RTT** | 214.83 ms |
| **T_Proc Worker** | 198.91 ms |
| **RAM Máxima** | 281.29 MB |
| **CPU Máxima** | 196.52 % |
| **Payload Red** | 2.99 MB |

---

