``` mermaid
flowchart TD
    Internet((Internet))

    subgraph Maquina1 ["Màquina 1: Orquestrador (Màster + K3s Server)"]
        direction TB
        Ansible["Pla de Control:<br>Ansible (Gestió Declarativa)"]
        KubeAPI["Pla d'Orquestració:<br>Kubernetes API (K3s)"]
        Padre["Pla de Dades:<br>Script Màster (PyTorch)<br>+<br>Fase 2b: Entrena la CNN localment"]
    end

    Ansible ~~~ Padre
    Padre ~~~ KubeAPI
    

    subgraph Worker2 ["Node: Worker 2 (192.168.98.144)"]
        K3sB["K3s Agent (containerd + Kubelet)"]
        Hijo2["Pod d'Inferència"]
        K3sB -- "Cicle de vida" --> Hijo2
    end

    subgraph Worker1 ["Node: Worker 1 (192.168.98.143)"]
        K3sA["K3s Agent (containerd + Kubelet)"]
        Hijo1["Pod d'Inferència"]
        K3sA -- "Cicle de vida" --> Hijo1
    end

    %% FASE 1: Aprovisionament (Ansible SEMPRE discontínua)
    Ansible -. "Fase 1a: Configura l'entorn" .-> Padre
    Ansible -. "Fase 1b: SSH, injecta .tar<br>(Air-Gapped)" .-> Worker1
    Ansible -. "Fase 1b: SSH, injecta .tar<br>(Air-Gapped)" .-> Worker2
    Ansible -. "Fase 1c: Aplica el manifest YAML" .-> KubeAPI

    %% FASE D'ORQUESTRACIÓ (Kubernetes actiu)
    KubeAPI <==>|Gestió contínua: Heartbeat, <br>Reconciliació i Estat| K3sA
    KubeAPI <==>|Gestió contínua: Heartbeat, <br>Reconciliació i Estat| K3sB

    %% FASE 2: Dataset
    Internet -- "Fase 2a: Descarrega MNIST" --> Padre

    %% FASES 3: Establiment de protocols
    Padre -- "Fase 3: Estableix protocols<br>(HTTP/gRPC/ZMQ)" --> Hijo1
    Padre -- "Fase 3: Estableix protocols<br>(HTTP/gRPC/ZMQ)" --> Hijo2

    %% FASES 4: Flux d'anada
    Padre -- "Fase 4: Envia dades<br>i model (.pth)<br>(Servei NodePort)" --> Hijo1
    Padre -- "Fase 4: Envia dades<br>i model (.pth)<br>(Servei NodePort)" --> Hijo2

    %% FASES 5: Flux de tornada
    Hijo1 -- "Fase 5: Retorna<br>predicció i mètriques" --> Padre
    Hijo2 -- "Fase 5: Retorna<br>predicció i mètriques" --> Padre

    %% Estils
    classDef control fill:#f3e5f5,stroke:#8e24aa,color:#000;
    classDef datos fill:#e1f5fe,stroke:#039be5,color:#000;
    classDef worker fill:#f1f8e9,stroke:#689f38,color:#000;
    classDef kube fill:#e8eaf6,stroke:#3f51b5,stroke-width:3px,color:#000;
    class Ansible control; class Padre datos; class Hijo1,Hijo2 worker; class KubeAPI,K3sA,K3sB kube;
```