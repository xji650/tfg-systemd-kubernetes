# [Orchestration Trade-offs in Edge Computing: systemd vs Kubernetes](https://xji650.github.io/tfg-systemd-kubernetes/#/)

Trabajo de Fin de Grado centrado en el análisis comparativo de mecanismos de orquestación para entornos edge.

## Descripción

Este repositorio contiene la documentación técnica del proyecto de fin de grado, que evalúa los trade-offs entre Kubernetes y systemd como soluciones de orquestación para nodos edge.

Los entornos edge presentan desafíos específicos: recursos computacionales limitados, requisitos de despliegue simplificado y necesidad de baja latencia. Este estudio analiza ambas tecnologías mediante experimentos controlados que miden:

- **Rendimiento**: Consumo de CPU, memoria y tiempo de arranque de servicios
- **Resiliencia**: Comportamiento ante fallos de red, reinicios de contenedores y saturación de recursos
- **Complejidad de gestión**: Curva de aprendizaje, mantenimiento operativo y automatización
- **Facilidad de despliegue**: Configuración inicial y requisitos de infraestructura

## Estructura de la documentación

```
Project-TFG/
├── index.html                    # Punto de entrada de Docsify
├── _sidebar.md                   # Navegación lateral
├── Setmana0_setup-mv/           # Configuración inicial de nodos (máquinas virtuales)
├── Setmana1_podman/             # Instalación y gestión con Podman
├── Setmana2_systemd-legacy/     # Orquestación con systemd tradicional
├── Setmana3.1_systemd-quadlets/ # Systemd con Quadlets (nativo para contenedores)
├── Setmana5_kubernetes/         # Despliegue con K3s/Kubernetes
├── entrega-1/                   # Setup Ansible + Systemd + Podman
└── entrega-2/                   # Análisis comparativo Systemd + Podman
```

## Navegación

| Sección | Contenido |
|---------|-----------|
| Setup | Preparación del entorno: máquinas virtuales, configuración de red y herramientas base |
| Podman | Instalación, configuración y gestión de contenedores sin daemon |
| Systemd | Orquestación con unidades .service y .pod (Quadlets) |
| Kubernetes | Despliegue de clúster ligero con K3s y manifiestos YAML |
| Entregas | Resultados de experimentos: HTTP, gRPC, ZeroMQ y análisis comparativo |

## Visualización de la documentación

### 1. En Localhost (Dev)

```bash
docsify serve .
```
Accede en: http://localhost:3000

### 2. En el navegador (Prod)

Acceder en: https://xji650.github.io/tfg-systemd-kubernetes/#/

---

### Requisitos

- Node.js >= 14
- Navegador moderno (Chrome, Firefox, Edge, Safari)

## Metodología de experimentación

Los experimentos se diseñaron para simular escenarios edge realistas:

1. **Cargas de trabajo representativas**: Servicios HTTP, gRPC y ZeroMQ
2. **Inyección de fallos**: Cortes de red, reinicios de contenedores, saturación de CPU/memoria
3. **Métricas evaluadas**:
   - Tiempo de recuperación ante fallos
   - Overhead de recursos en estado estable
   - Complejidad de configuración (archivos y líneas de código necesarias)

## Resultados principales

- **systemd + Quadlets**: Adecuado para nodos edge con pocos servicios (1-3), mínimo consumo de recursos base y integración nativa con el sistema operativo.

- **Kubernetes (K3s)**: Recomendable cuando se requiere escalado automático, gestión centralizada de múltiples nodos o integración con ecosistema cloud-native.

- **Trade-off identificado**: La mayor automatización y abstracción de Kubernetes implica un consumo de recursos base superior, lo que puede ser limitante en hardware edge muy restringido.

Consultar los informes detallados en las carpetas `entrega-1/` y `entrega-2/`.

## Tecnologías utilizadas

| Herramienta | Propósito |
|-------------|-----------|
| Podman | Gestión de contenedores sin root ni daemon |
| systemd | Orquestación nativa en Linux con soporte para Quadlets |
| K3s | Distribución ligera de Kubernetes optimizada para edge |
| Ansible | Automatización de despliegues y configuración de nodos |
| Docsify | Generación de documentación estática basada en Markdown |

## Licencia

Este proyecto utiliza un modelo de licencias dual:

- **Código y scripts** (Ansible, Kubernetes, systemd, shell): [MIT License](LICENSE)
- **Documentación y textos** (.md, README, informes): [CC BY-SA 4.0](LICENSE)

Este proyecto se publica con fines académicos. Consulte el archivo LICENSE para más detalles.

---

Documentación generada con [Docsify](https://docsify.js.org/).  
Repositorio: [Github](https://github.com/xji650/tfg-systemd-kubernetes)
