``` mermaid
flowchart TD
    Internet((Internet))

    subgraph Maquina1 ["Máquina 1: Orquestador MLOps (Master)"]
        direction TB
        Ansible["Plano de Control:<br>Ansible Playbooks"]
        Padre["Plano de Datos: 
        Script Master (PyTorch) 
        + 
        Fase 2b: Entrena CNN localmente"]
        
        Ansible -. "Fase 1: Configura entorno" .-> Padre
    end

    subgraph NodosEdge ["Capa de Ejecución (Workers Edge)"]
        direction LR
        Hijo1["Worker 1 (192.168.98.143)
        Contenedor de Inferencia"]
        Hijo2["Worker 2 (192.168.98.144)
        Contenedor de Inferencia"]
    end

    %% FASE 1: Aprovisionamiento
    Ansible -- "Fase 1 SSH: 
    Despliega Podman y Quadlets" --> Hijo1
    Ansible -- "Fase 1 SSH: 
    Despliega Podman y Quadlets" --> Hijo2

    %% FASE 2: Dataset
    Internet -- "Fase 2a: Descarga MNIST" --> Padre

    %% FASES 3 y 4: FLUJO DE IDA (Línea Continua)
    Padre -- "Fase 3: Envía Modelo (.pth)

    Fase 4: Envía Datos 
    (HTTP/gRPC/ZMQ)" --> Hijo1

    Padre -- "Fase 3: Envía Modelo (.pth)

    Fase 4: Envía Datos 
    (HTTP/gRPC/ZMQ)" --> Hijo2

    %% FASE 5: FLUJO DE VUELTA (Línea Punteada para evitar colapso del motor)
    Hijo1 -. "Fase 5: Devuelve 
    Predicciones y Metricas" .-> Padre
    
    Hijo2 -. "Fase 5: Devuelve 
    Predicciones y Metricas" .-> Padre

    %% Estilos (Con contraste forzado)
    classDef control fill:#f3e5f5,stroke:#8e24aa,stroke-width:2px,color:#000;
    classDef datos fill:#e1f5fe,stroke:#039be5,stroke-width:2px,color:#000;
    classDef worker fill:#f1f8e9,stroke:#689f38,stroke-width:2px,color:#000;
    classDef edgeCapa fill:#fafafa,stroke:#bdbdbd,stroke-width:2px,stroke-dasharray: 5 5,color:#000;

    class Ansible control;
    class Padre datos;
    class Hijo1,Hijo2 worker;
    class NodosEdge edgeCapa;
```