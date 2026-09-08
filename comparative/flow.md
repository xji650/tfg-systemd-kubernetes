``` mermaid
    flowchart TD
        Start([Inici de l'Orquestrador Mestre]) --> F1_Init

        subgraph Fase 1: Entorn Natiu - Systemd
            F1_Init[Apagar i bloquejar agent K3s als Workers] --> F1_Loop
            F1_Loop{Iteració Màster} -->|Inici cicle| F1_Reboot[Reboot físic dels nodes]
            F1_Reboot --> F1_Cool[Refredament tèrmic 120s]
            F1_Cool --> F1_Bench[Executar sub-orquestrador Systemd]
            F1_Bench --> F1_Loop
        end

        F1_Loop -->|Fi de les iteracions| F2_Init

        subgraph Fase 2: Entorn Distribuït - K3s
            F2_Init[Purga de l'entorn Systemd via Ansible] --> F2_StartK3s[Reactivar agent K3s als Workers]
            F2_StartK3s --> F2_Loop
            F2_Loop{Iteració Màster} -->|Inici cicle| F2_Reboot[Reboot físic dels nodes]
            F2_Reboot --> F2_Cool[Refredament tèrmic 120s]
            F2_Cool --> F2_Bench[Executar sub-orquestrador K3s]
            F2_Bench --> F2_Loop
        end

        F2_Loop -->|Fi de les iteracions| F3_Init

        subgraph Fase 3: Consolidació i Resultats
            F3_Init[Unificar els Data Lakes CSV] --> F3_Graph[Generar gràfiques comparatives amb Python]
        end

        F3_Graph --> Finish([Procés Completat])

```