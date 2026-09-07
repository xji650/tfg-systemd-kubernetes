# Resultados Consolidados del Proyecto
> **Nota:** Estas tablas representan la **media histórica total** de todas las ejecuciones almacenadas en el Data Lake (`resultados-globales.csv`).

## Protocolo: 01-http-json (Basado en 6 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 175.26 s |
| **Recuperación (MTTR)** | 491.53 ms |
| **CPU Reposo** | 0.08 % |
| **RAM Reposo** | 729.92 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.80 s |
| **Throughput** | 2492.71 img/s |
| **Latencia RTT** | 416.45 ms |
| **T_Proc Worker** | 402.00 ms |
| **RAM Máxima** | 329.12 MB |
| **CPU Máxima** | 141.84 % |
| **Payload Red** | 15.59 MB |

---

## Protocolo: 02-grpc-protobuf (Basado en 6 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 173.77 s |
| **Recuperación (MTTR)** | 494.71 ms |
| **CPU Reposo** | 0.42 % |
| **RAM Reposo** | 736.92 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.23 s |
| **Throughput** | 8621.28 img/s |
| **Latencia RTT** | 223.62 ms |
| **T_Proc Worker** | 198.63 ms |
| **RAM Máxima** | 311.62 MB |
| **CPU Máxima** | 197.20 % |
| **Payload Red** | 2.99 MB |

---

## Protocolo: 03-zeromq-protobuf (Basado en 6 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 111.93 s |
| **Recuperación (MTTR)** | 491.86 ms |
| **CPU Reposo** | 0.08 % |
| **RAM Reposo** | 721.08 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.22 s |
| **Throughput** | 9299.01 img/s |
| **Latencia RTT** | 212.55 ms |
| **T_Proc Worker** | 197.79 ms |
| **RAM Máxima** | 275.61 MB |
| **CPU Máxima** | 197.11 % |
| **Payload Red** | 2.99 MB |

---

## Protocolo: 04-zeromq-messagepack (Basado en 6 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 199.40 s |
| **Recuperación (MTTR)** | 483.44 ms |
| **CPU Reposo** | 0.00 % |
| **RAM Reposo** | 729.50 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.22 s |
| **Throughput** | 9079.08 img/s |
| **Latencia RTT** | 214.71 ms |
| **T_Proc Worker** | 198.58 ms |
| **RAM Máxima** | 280.28 MB |
| **CPU Máxima** | 196.38 % |
| **Payload Red** | 2.99 MB |

---

