# Resultados Consolidados del Proyecto
> **Nota:** Estas tablas representan la **media histórica total** de todas las ejecuciones almacenadas en el Data Lake (`resultados-globales.csv`).

## Protocolo: 01-http-json (Basado en 9 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 116.35 s |
| **Recuperación (MTTR)** | 1508.39 ms |
| **CPU Reposo** | 0.89 % |
| **RAM Reposo** | 833.78 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 1.04 s |
| **Throughput** | 1985.05 img/s |
| **Latencia RTT** | 543.41 ms |
| **T_Proc Worker** | 530.54 ms |
| **RAM Máxima** | 341.83 MB |
| **CPU Máxima** | 139.25 % |
| **Payload Red** | 15.59 MB |

---

## Protocolo: 02-grpc-protobuf (Basado en 9 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 131.26 s |
| **Recuperación (MTTR)** | 57372.86 ms |
| **CPU Reposo** | 0.78 % |
| **RAM Reposo** | 809.11 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.34 s |
| **Throughput** | 6150.54 img/s |
| **Latencia RTT** | 332.08 ms |
| **T_Proc Worker** | 298.75 ms |
| **RAM Máxima** | 380.99 MB |
| **CPU Máxima** | 186.04 % |
| **Payload Red** | 2.99 MB |

---

## Protocolo: 03-zeromq-protobuf (Basado en 9 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 91.40 s |
| **Recuperación (MTTR)** | 1615.15 ms |
| **CPU Reposo** | 0.78 % |
| **RAM Reposo** | 838.33 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.31 s |
| **Throughput** | 6883.04 img/s |
| **Latencia RTT** | 269.05 ms |
| **T_Proc Worker** | 206.91 ms |
| **RAM Máxima** | 283.75 MB |
| **CPU Máxima** | 192.91 % |
| **Payload Red** | 2.99 MB |

---

## Protocolo: 04-zeromq-messagepack (Basado en 9 tests históricos)
### Infraestructura
| Métrica | Valor Promedio |
|---|---|
| **T_deploy** | 141.21 s |
| **Recuperación (MTTR)** | 1441.10 ms |
| **CPU Reposo** | 0.72 % |
| **RAM Reposo** | 835.56 MB |

### Rendimiento de Red (Estrés)
| Métrica | Valor Promedio |
|---|---|
| **T_Total** | 0.33 s |
| **Throughput** | 6582.80 img/s |
| **Latencia RTT** | 276.94 ms |
| **T_Proc Worker** | 208.03 ms |
| **RAM Máxima** | 277.06 MB |
| **CPU Máxima** | 194.04 % |
| **Payload Red** | 2.99 MB |

---

