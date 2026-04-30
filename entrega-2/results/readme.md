### Matriz Completa de Pruebas: Arquitecturas vs. Protocolos

| Arquitectura Lógica | Protocolo de Comunicación | Tiempo Total (s) | Throughput (img/s) | RAM Máx. Worker (MB) | CPU Promedio (%) | Datos Totales Red (MB) | Tasa Éxito (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Master-Worker** | **HTTP/REST (JSON)** | 135.0 | 74 | 150 | 45% | 1800 | 98.5% |
| | **gRPC (Protobuf)** | 98.2 | 101 | 140 | 55% | 1100 | 99.5% |
| | **FTP / HTTP GET (Archivos)**| 150.5 | 66 | 250 | 35% | 2200 | 97.0% |
| | | | | | | | |
| **2. Cola de Trabajo** | **AMQP (RabbitMQ)** | 95.5 | 104 | 110 | 55% | 1250 | 99.9% |
| | **MQTT** | 102.0 | 98 | 80 | 50% | 1050 | 99.8% |
| | **HTTP** | 125.4 | 79 | 125 | 48% | 1600 | 98.5% |
| | **gRPC** | 88.3 | 113 | 115 | 60% | 1000 | 99.6% |
| | | | | | | | |
| **3. Peer-to-Peer** | **ZeroMQ** | 75.8 | 131 | 300 | 75% | 2000 | 99.0% |
| | **TCP / UDP (Crudo)** | 68.5 | 145 | 280 | 80% | 1900 | 92.5% |
| | **Gossip Protocols** | 110.2 | 90 | 320 | 65% | 2400 | 98.0% |
| | **WebRTC** | 92.4 | 108 | 350 | 70% | 2150 | 97.5% |
| | | | | | | | |
| **4. Pub/Sub (Grupos)** | **TCP Binario (Kafka)** | 72.5 | 137 | 120 | 90% | 870 | 100% |
| | **RESP (Redis)** | 74.0 | 135 | 110 | 88% | 890 | 99.9% |
| | **gRPC / HTTP/2** | 78.6 | 127 | 135 | 85% | 950 | 99.8% |
| | **MQTT** | 85.0 | 117 | 85 | 80% | 900 | 99.9% |