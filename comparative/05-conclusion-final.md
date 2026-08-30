# Comparativa Arquitectónica en el Edge: Systemd vs Kubernetes (K3s)

Este documento presenta la conclusión técnica del proyecto, enfrentando la arquitectura nativa basada en Systemd frente al orquestador moderno Kubernetes (K3s). Para garantizar una evaluación equitativa, ambas plataformas se han sometido a pruebas de estrés utilizando el protocolo de red más eficiente identificado en fases anteriores: **ZeroMQ con serialización MessagePack**.

El objetivo de esta comparativa es cuantificar el "Impuesto Arquitectónico" (*Architectural Overhead*) que introduce Kubernetes al ser desplegado en hardware de recursos limitados (Edge Computing) frente a soluciones de ejecución nativa.

## 1. El Impuesto Arquitectónico (Consumo de RAM en Reposo)

La primera métrica evaluada es el consumo base de la infraestructura antes de inyectar carga de trabajo, medido a nivel del sistema operativo.

![Consumo de RAM en Reposo](./visualizations_final/1_overhead_ram.png)

* **Análisis:** La arquitectura basada en Systemd presenta un consumo medio en reposo de ~730 MB. La adopción de Kubernetes eleva esta base a ~850 MB.
* **Justificación Técnica:** Esta diferencia de ~120 MB constituye el impuesto directo del orquestador. Mientras que Systemd ejecuta los contenedores de forma nativa interactuando directamente con el *kernel*, K3s requiere mantener activos múltiples demonios en segundo plano para sostener el estado del clúster (*kubelet*, plano de control API, *containerd* y el controlador de red *flannel*). En dispositivos perimetrales con 2 GB o 4 GB de RAM, esta reserva permanente de memoria reduce significativamente el margen disponible para el procesamiento de cargas de Inteligencia Artificial (*Compute Bound*).

## 2. Ingeniería del Caos y Resiliencia (MTTR)

Para evaluar la capacidad de auto-recuperación ante fallos críticos, se aplicó un protocolo de *Chaos Testing*, eliminando abruptamente los contenedores (`kill -9` en Systemd y `delete pod --force` en K3s) y midiendo el Tiempo Medio de Recuperación (MTTR).

![Resiliencia MTTR](./visualizations_final/2_mttr_resiliencia.png)

* **Análisis:** Systemd demuestra una velocidad de recuperación superior, reiniciando el servicio en ~490 ms. Kubernetes, por su parte, requiere ~1600 ms (más del triple de tiempo).
* **Justificación Técnica:** Systemd gestiona los procesos directamente a nivel de *kernel* como demonios locales, lo que permite un reinicio casi instantáneo. Kubernetes opera bajo un modelo distribuido asíncrono: el bucle de reconciliación (*Reconciliation Loop*) debe detectar la caída a través de la API, el *Scheduler* debe reprogramar el Pod, y el *Kubelet* debe interactuar con el motor de contenedores y solicitar una nueva IP virtual al CNI, lo que añade latencia inherente al proceso de recuperación.

### 2.1. Tratamiento de Datos (Data Cleansing)

Durante la evaluación empírica del MTTR en Kubernetes, se registró un valor atípico (*Outlier*) extremo en una de las iteraciones (261.450 ms, aprox. 4 minutos). El análisis de los *logs* determinó que este evento no fue un fallo del protocolo de IA, sino un bloqueo temporal (*lock*) en la liberación de la IP virtual por parte del plugin de red Flannel tras la destrucción abrupta del Pod.

![Resiliencia MTTR Outlier](./visualizations_final/2_mttr_resiliencia_original.png)

Para mantener la integridad estadística de la comparativa y aislar el rendimiento real del orquestador frente a fallos transitorios de infraestructura, se aplicó una técnica de imputación de la media (*Data Cleansing*), sustituyendo este valor anómalo por el promedio de las ejecuciones estables.

## 3. Penalización de Red Virtual (Rendimiento y Throughput)

La prueba final evalúa el impacto de la capa de infraestructura sobre el rendimiento bruto de la red bajo estrés máximo.

![Penalización de Red](./visualizations_final/3_throughput_comparativa.png)

* **Análisis:** Utilizando el mismo código fuente, Systemd alcanza un procesamiento superior a las ~9.300 imágenes por segundo, frente a las ~6.500 img/s que logra Kubernetes.
* **Justificación Técnica:** Esta degradación de aproximadamente un 30% en el rendimiento (*Throughput*) es consecuencia directa de la capa SDN (*Software-Defined Networking*) de Kubernetes. En la arquitectura Systemd, los contenedores utilizan la red del *host* con acceso casi nativo a las interfaces físicas. En K3s, el tráfico inter-nodo debe ser encapsulado y procesado por Flannel (mediante túneles VXLAN), lo que introduce un coste adicional en ciclos de CPU para empaquetar y desempaquetar cada paquete TCP, mermando el ancho de banda efectivo para la aplicación.

## 4. Veredicto Final y Trade-Offs

La decisión entre Systemd y Kubernetes se reduce a una balanza estricta entre el rendimiento bruto del hardware y la complejidad operativa de tu flota de dispositivos.

**Cuándo apostar por Systemd (Arquitectura Nativa)**
Systemd es la elección indiscutible para despliegues perimetrales aislados (*Standalone*) donde los recursos físicos son ultra-limitados y el rendimiento es innegociable. Si tus nodos Edge cuentan con 2 GB de RAM o menos, debes optar por esta vía para evitar que un orquestador asfixie la memoria disponible para tu Inteligencia Artificial. Es la herramienta adecuada cuando tu prioridad absoluta es la velocidad, permitiéndote exprimir la red física hasta las ~9.300 imágenes por segundo, y cuando necesitas que un servicio caído se recupere localmente de forma casi instantánea. Systemd es perfecto mientras puedas permitirte gestionar los equipos mediante despliegues imperativos con herramientas externas como Ansible.

**El punto de inflexión: Cuándo Systemd ya no vale la pena**
El modelo nativo se rompe cuando la escala del proyecto convierte la administración en un cuello de botella. Systemd deja de ser viable en el momento en que pasas de gestionar un puñado de placas aisladas a administrar una red de decenas o cientos de dispositivos distribuidos. Mantener la configuración de red estática, actualizar versiones de contenedores nodo por nodo y carecer de un balanceador de carga integrado se vuelve insostenible. Además, Systemd tiene un límite físico fatal: si un nodo Edge se quema o pierde energía, el contenedor de IA muere con él, sin posibilidad de migrar automáticamente a otra máquina sana.

**Cuándo dar el salto a Kubernetes (K3s)**
Es en ese umbral de complejidad donde debes transicionar a Kubernetes, asumiendo su "impuesto arquitectónico" como el precio a pagar por la paz mental operativa. K3s es obligatorio cuando tu flota requiere despliegues dinámicos, gestión centralizada y actualizaciones automático. Aunque el orquestador eleve el consumo base a ~850 MB y penalice la red virtual mermando el ancho de banda un 30%, esta pérdida se justifica totalmente si tu sistema requiere alta disponibilidad a nivel de clúster. K3s transforma dispositivos individuales en una colmena; si un hardware falla, el orquestador reprogramará automáticamente su carga en otro nodo perimetral.

En conclusión: **Systemd se posiciona como la solución óptima para nodos Edge aislados con recursos ultra-limitados**, donde el rendimiento y la latencia son críticos. Por el contrario, **Kubernetes justifica su "impuesto arquitectónico" en escenarios donde prima la reducción de la complejidad de gestión operativa**, permitiendo despliegues dinámicos, tolerancia a fallos a nivel de red y actualizaciones *Zero-Touch* sobre flotas de dispositivos distribuidos.