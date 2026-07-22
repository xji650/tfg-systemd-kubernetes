``` mermaid
flowchart TD
    Internet((Internet))

    subgraph Maquina1 ["Máquina 1: Orquestador (Master + K3s Server)"]
        direction TB
        Ansible["Plano Control:<br>Ansible (Gestión Declarativa)"]
        KubeAPI["Plano de Orquestación:<br>Kubernetes API (K3s)"]
        Padre["Plano de Datos:<br>Script Master (PyTorch)<br>+<br>Fase 2b: Entrena CNN localmente"]
    end

    Ansible ~~~ Padre
    Padre ~~~ KubeAPI
    

    subgraph Worker2 ["Nodo: Worker 2 (192.168.98.144)"]
        K3sB["K3s Agent (containerd + Kubelet)"]
        Hijo2["Pod de Inferencia"]
        K3sB -- "Ciclo de vida" --> Hijo2
    end

    subgraph Worker1 ["Nodo: Worker 1 (192.168.98.143)"]
        K3sA["K3s Agent (containerd + Kubelet)"]
        Hijo1["Pod de Inferencia"]
        K3sA -- "Ciclo de vida" --> Hijo1
    end

    %% FASE 1: Aprovisionamiento (Ansible SIEMPRE discontinua)
    Ansible -. "Fase 1a: Configura entorno" .-> Padre
    Ansible -. "Fase 1b: SSH, inyecta .tar<br>(Air-Gapped)" .-> Worker1
    Ansible -. "Fase 1b: SSH, inyecta .tar<br>(Air-Gapped)" .-> Worker2
    Ansible -. "Fase 1c: Aplica manifiesto YAML" .-> KubeAPI

    %% FASE DE ORQUESTACIÓN (Kubernetes activo)
    KubeAPI <==>|Gestión continua: Heartbeat, <br>Reconciliación y Estado| K3sA
    KubeAPI <==>|Gestión continua: Heartbeat, <br>Reconciliación y Estado| K3sB

    %% FASE 2: Dataset
    Internet -- "Fase 2a: Descarga MNIST" --> Padre

    %% FASES 3: Establecer protocolos
    Padre -- "Fase 3: Establecer protocolos<br>(HTTP/gRPC/ZMQ)" --> Hijo1
    Padre -- "Fase 3: Establecer protocolos<br>(HTTP/gRPC/ZMQ)" --> Hijo2

    %% FASES 4: Fujo de ida
    Padre -- "Fase 4: Envía Datos<br>y Modelo (.pth)<br>(Service NodePort)" --> Hijo1
    Padre -- "Fase 4: Envía Datos<br>y Modelo (.pth)<br>(Service NodePort)" --> Hijo2

    %% FASES 5: Fujo de vuelta
    Hijo1 -- "Fase 5: Devuelve<br>Predicción y Métricas" --> Padre
    Hijo2 -- "Fase 5: Devuelve<br>Predicción y Métricas" --> Padre

    %% Estilos
    classDef control fill:#f3e5f5,stroke:#8e24aa,color:#000;
    classDef datos fill:#e1f5fe,stroke:#039be5,color:#000;
    classDef worker fill:#f1f8e9,stroke:#689f38,color:#000;
    classDef kube fill:#e8eaf6,stroke:#3f51b5,stroke-width:3px,color:#000;
    class Ansible control; class Padre datos; class Hijo1,Hijo2 worker; class KubeAPI,K3sA,K3sB kube;
```