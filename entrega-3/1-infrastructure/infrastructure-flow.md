``` mermaid
graph LR
    %% Clases de estilo para darle un toque profesional
    classDef master fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
    classDef worker fill:#f1f8e9,stroke:#2e7d32,stroke-width:2px;
    classDef files fill:#fff,stroke:#333,stroke-width:1px,stroke-dasharray: 4 4;

    subgraph Control_Node ["Máquina de Control (Master)"]
        Orchestrator[Orquestador Ansible]:::master
        ImageArtifact[tmp/worker-mnist.tar]:::files
    end

    subgraph Edge_Node ["Nodo Perimetral (Worker)"]
        SystemdEnv[Entorno Systemd<br>Linger + Carpetas]:::worker
        Network[red.network]:::files
        Registry[(Registry Local Podman)]:::worker
        ContainerService((worker.service)):::worker
    end

    %% Fases consolidadas para evitar cruces
    Orchestrator -->|Fase 1: Persistencia| SystemdEnv
    SystemdEnv -.->|Configura| Network

    Orchestrator -->|Fase 2: Build & Save| ImageArtifact

    ImageArtifact -->|Fase 3: SCP & Load| Registry

    Orchestrator -->|Fase 4: Deploy & Reload| ContainerService
    Network -.->|Requiere| ContainerService
    Registry -.->|Provee imagen| ContainerService
```