``` mermaid
flowchart TD
    Internet((Internet))

    subgraph Maquina1 ["Máquina 1: Orquestador (Master)"]
        direction TB
        Ansible["Plano Control:<br>Ansible (Gestión Imperativa)"]
        
        Padre["Plano de Datos: 
        Script Master (PyTorch) 
        + 
        Fase 2b: Entrena CNN localmente"]
    end

    Padre ~~~ NodeA
    Padre ~~~ NodeB

    subgraph NodeB ["Nodo Worker 2: 192.168.98.144"]
        Sys1(("Systemd<br>(Gestor Local)"))
        Hijo2["Contenedor Podman"]
        Sys1 -- "Ciclo de vida<br>(Local)" --> Hijo2
    end
    
    subgraph NodeA ["Nodo Worker 1: 192.168.98.143"]
        Sys2(("Systemd<br>(Gestor Local)"))
        Hijo1["Contenedor Podman"]
        Sys2 -- "Ciclo de vida<br>(Local)" --> Hijo1
    end


    %% FASE 1: Aprovisionamiento
    Ansible -. "Fase 1a: Configura entorno" .-> Padre
    Ansible -. "Fase 1b SSH:<br> Despliega Podman y Quadlets" .-> NodeB
    Ansible -. "Fase 1b SSH:<br> Despliega Podman y Quadlets" .-> NodeA

    %% FASE 2: Modelo IA
    Internet -- "Fase 2a: Descarga MNIST" --> Padre

    %% FASES 3: Establecer protocolos
    Padre -- "Fase 3: Establecer protocolos<br>(HTTP/gRPC/ZMQ)" --> Hijo2
    Padre -- "Fase 3: Establecer protocolos<br>(HTTP/gRPC/ZMQ)" --> Hijo1

    %% FASES 4: Fujo de ida
    Padre -- "Fase 4: Envía Datos<br>y Modelo (.pth)" --> Hijo2
    Padre -- "Fase 4: Envía Datos<br>y Modelo (.pth)" --> Hijo1

    %% FASES 5: Fujo de vuelta
    Hijo2 -- "Fase 5: Devuelve<br>Predicción y Métricas" --> Padre
    Hijo1 -- "Fase 5: Devuelve<br>Predicción y Métricas" --> Padre

    classDef control fill:#f3e5f5,stroke:#8e24aa,color:#000;
    classDef datos fill:#e1f5fe,stroke:#039be5,color:#000;
    classDef worker fill:#f1f8e9,stroke:#689f38,color:#000;
    classDef sys fill:#fff9c4,stroke:#fbc02d,color:#000;
    class Ansible control; class Padre datos; class Hijo1,Hijo2 worker; class Sys1,Sys2 sys;
    
```