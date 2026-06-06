import zmq
import psutil
import os
import numpy as np
import time
import mnist_pb2

def serve():
    context = zmq.Context()
    # Socket para responder (REPLY)
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:8000") # Puerto definido en tu infraestructura
    
    process = psutil.Process(os.getpid())
    process.cpu_percent(interval=None) # Inicialización obligatoria
    
    print("Worker ZeroMQ listo en puerto 8000...")

    while True:
        # Recibir mensaje (bytes de Protobuf)
        message_bytes = socket.recv()
        
        # 1. Limpieza de buffer de CPU para esta petición
        process.cpu_percent(interval=None)
        start_proc = time.perf_counter()
        
        # 2. Deserializar usando el contrato
        request = mnist_pb2.BatchRequest()
        request.ParseFromString(message_bytes)
        
        # 3. Procesamiento
        datos = np.frombuffer(request.image_data, dtype=np.float32)
        cantidad = len(datos) // 784
        
        # 4. Métricas
        ram_usage = process.memory_info().rss / (1024 * 1024)
        cpu_usage = process.cpu_percent(interval=None)
        
        end_proc = time.perf_counter()
        t_proc_ms = (end_proc - start_proc) * 1000
        
        # Preparar respuesta Protobuf
        response = mnist_pb2.BatchResponse(
            batch_id=request.batch_id,
            images_processed=int(cantidad),
            status="OK",
            ram_usage=float(ram_usage),
            cpu_usage=float(cpu_usage),
            t_proc_ms=float(t_proc_ms)
        )
        
        # Enviar respuesta como bytes
        socket.send(response.SerializeToString())
        
        # --- LOG COMPLETO PARA SYSTEMD ---
        print(f"ZMQ: Procesadas {int(cantidad)} img. RAM: {ram_usage:.2f}MB, CPU: {cpu_usage}%, T_proc: {t_proc_ms:.2f}ms")

if __name__ == "__main__":
    serve()