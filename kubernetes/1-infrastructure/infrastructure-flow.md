``` mermaid
graph LR
    %% Clases d'estil amb els colors de lletra corregits per a un bon contrast
    classDef master fill:#2255ff,stroke:#1565c0,stroke-width:2px,color:#ffffff;
    classDef worker fill:#2f1fe9,stroke:#2e7d32,stroke-width:2px,color:#ffffff;
    classDef files fill:#f2f2f2,stroke:#333,stroke-width:1px,stroke-dasharray: 4 4,color:#000000;
    classDef k8s fill:#032e1a,stroke:#8f91b5,stroke-width:2px,color:#ffffff;

    subgraph Control_Node ["Màquina de Control (Master)"]
        Orchestrator[Orquestrador Ansible]:::master
        ImageArtifact[tmp/worker-mnist.tar]:::files
        Manifest[deployment.yaml]:::files
        KubeAPI((K3s API Server)):::k8s
    end

    subgraph Edge_Node ["Node Perimetral (Worker)"]
        Containerd[(Containerd<br>Magatzem d'Imatges)]:::worker
        Kubelet[Kubelet<br>Agent K3s]:::k8s
        Pod((Pod d'Inferència)):::worker
    end

    %% Fases consolidades
    Orchestrator -->|Fase 1: Construcció i Desa| ImageArtifact
    
    %% Injecció física
    ImageArtifact -->|Fase 2: SSH + Injecció <br> Air-Gapped| Containerd
    
    %% Gestió lògica
    Orchestrator -->|Fase 3: kubectl apply| Manifest
    Manifest -.->|Defineix l'Estat Desitjat| KubeAPI
    
    %% Orquestració
    KubeAPI ==>|Fase 4: Reconciliació| Kubelet
    Kubelet -.->|Gestiona el Cicle de Vida| Pod
    Containerd -.->|Proveeix la imatge local| Pod
```