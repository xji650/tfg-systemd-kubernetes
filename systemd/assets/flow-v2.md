``` mermaid
flowchart TD
    Internet((Internet))

    subgraph Maquina1 ["Màquina 1: Orquestrador (Màster)"]
        direction TB
        Ansible["Pla de Control:<br>Ansible (Gestió Imperativa)"]
        
        Padre["Pla de Dades: 
        Script Màster (PyTorch) 
        + 
        Fase 2b: Entrena la CNN localment"]
    end

    Padre ~~~ NodeA
    Padre ~~~ NodeB

    subgraph NodeB ["Node Worker 2: 192.168.98.144"]
        Sys1(("Systemd<br>(Gestor Local)"))
        Hijo2["Contenidor Podman"]
        Sys1 -- "Cicle de vida<br>(Local)" --> Hijo2
    end
    
    subgraph NodeA ["Node Worker 1: 192.168.98.143"]
        Sys2(("Systemd<br>(Gestor Local)"))
        Hijo1["Contenidor Podman"]
        Sys2 -- "Cicle de vida<br>(Local)" --> Hijo1
    end


    %% FASE 1: Aprovisionament
    Ansible -. "Fase 1a: Configura l'entorn" .-> Padre
    Ansible -. "Fase 1b SSH:<br> Desplega Podman i Quadlets" .-> NodeB
    Ansible -. "Fase 1b SSH:<br> Desplega Podman i Quadlets" .-> NodeA

    %% FASE 2: Model d'IA
    Internet -- "Fase 2a: Descarrega MNIST" --> Padre

    %% FASES 3: Establiment de protocols
    Padre -- "Fase 3: Estableix protocols<br>(HTTP/gRPC/ZMQ)" --> Hijo2
    Padre -- "Fase 3: Estableix protocols<br>(HTTP/gRPC/ZMQ)" --> Hijo1

    %% FASES 4: Flux d'anada
    Padre -- "Fase 4: Envia dades<br>i model (.pth)" --> Hijo2
    Padre -- "Fase 4: Envia dades<br>i model (.pth)" --> Hijo1

    %% FASES 5: Flux de tornada
    Hijo2 -- "Fase 5: Retorna<br>predicció i mètriques" --> Padre
    Hijo1 -- "Fase 5: Retorna<br>predicció i mètriques" --> Padre

    classDef control fill:#f3e5f5,stroke:#8e24aa,color:#000;
    classDef datos fill:#e1f5fe,stroke:#039be5,color:#000;
    classDef worker fill:#f1f8e9,stroke:#689f38,color:#000;
    classDef sys fill:#fff9c4,stroke:#fbc02d,color:#000;
    class Ansible control; class Padre datos; class Hijo1,Hijo2 worker; class Sys1,Sys2 sys;
    
```