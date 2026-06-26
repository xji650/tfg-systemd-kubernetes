``` mermaid
flowchart TD
    Internet((Internet))

    subgraph Maquina1 ["Máquina 1: Master / Padre"]
        direction TB
        Ansible["Plano de Control:<br>Ansible Playbooks"]
        Padre["Plano de Datos:<br>Contenedor Padre Podman"]
        
        Ansible -. "Fase 1: Configura a sí mismo<br>(Quadlets, systemd)" .-> Padre
    end

    subgraph Maquina2 ["Máquina 2: Worker 1"]
        Hijo1["Contenedor Hijo 1"]
    end

    subgraph Maquina3 ["Máquina 3: Worker 2"]
        Hijo2["Contenedor Hijo 2"]
    end

    %% FASE 1: Aprovisionamiento (Ansible a Hijos)
    Ansible -- "Fase 1 SSH: Configura y arranca" --> Hijo1
    Ansible -- "Fase 1 SSH: Configura y arranca" --> Hijo2

    %% FASE 2: Dataset
    Internet -- "Fase 2: Descarga MNIST" --> Padre

    %% FASE 3 y 4: Procesamiento (Protocolos a evaluar)
    Padre -- "Fase 3: Envía fragmentos<br>(HTTP, gRPC, MQTT...)" --> Hijo1
    Hijo1 -- "Fase 4: Recibe resultados<br>(HTTP, gRPC, MQTT...)" --> Padre

    Padre -- "Fase 3: Envía fragmentos<br>(HTTP, gRPC, MQTT...)" --> Hijo2
    Hijo2 -- "Fase 4: Recibe resultados<br>(HTTP, gRPC, MQTT...)" --> Padre

    %% Estilos (Añadido color:#000 para forzar contraste en Docsify)
    classDef control fill:#f3e5f5,stroke:#8e24aa,stroke-width:2px,color:#000;
    classDef datos fill:#e1f5fe,stroke:#039be5,stroke-width:2px,color:#000;
    classDef worker fill:#f1f8e9,stroke:#689f38,stroke-width:2px,color:#000;

    class Ansible control;
    class Padre datos;
    class Hijo1,Hijo2 worker;
```