``` mermaid
graph LR
    %% Clases de estilo para darle un toque profesional
    classDef master fill:#22fd,stroke:#1565c0,stroke-width:2px;
    classDef worker fill:#2f1fe9,stroke:#2e7d32,stroke-width:2px;
    classDef files fill:#f2f2,stroke:#333,stroke-width:1px,stroke-dasharray: 4 4;
    classDef k8s fill:#032e1a,stroke:#8f91b5,stroke-width:2px;

    subgraph Control_Node ["Máquina de Control (Master)"]
        Orchestrator[Orquestador Ansible]:::master
        ImageArtifact[tmp/worker-mnist.tar]:::files
        Manifest[deployment.yaml]:::files
        KubeAPI((K3s API Server)):::k8s
    end

    subgraph Edge_Node ["Nodo Perimetral (Worker)"]
        Containerd[(Containerd<br>Image Store)]:::worker
        Kubelet[Kubelet<br>K3s Agent]:::k8s
        Pod((Pod de Inferencia)):::worker
    end

    %% Fases consolidadas
    Orchestrator -->|Fase 1: Build & Save| ImageArtifact
    
    %% Inyección física
    ImageArtifact -->|Fase 2: SSH + Inyección <br> Air-Gapped| Containerd
    
    %% Gestión lógica
    Orchestrator -->|Fase 3: kubectl apply| Manifest
    Manifest -.->|Define Estado Deseado| KubeAPI
    
    %% Orquestación
    KubeAPI ==>|Fase 4: Reconciliación| Kubelet
    Kubelet -.->|Gestiona Ciclo de Vida| Pod
    Containerd -.->|Provee imagen local| Pod
```