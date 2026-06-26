import grpc
from concurrent import futures
import psutil
import os
import numpy as np
import time
import mnist_pb2
import mnist_pb2_grpc

class MnistServicer(mnist_pb2_grpc.MnistServiceServicer):
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.process.cpu_percent(interval=None) # Inicialización obligatoria

    def ProcessBatch(self, request, context):
        # 1. Limpieza de buffer de CPU
        self.process.cpu_percent(interval=None)
        
        # Inicio cronómetro de procesamiento
        start_proc = time.perf_counter()
        
        # 2. Deserialización binaria (¡Esto debería ser mucho más rápido que JSON!)
        datos = np.frombuffer(request.image_data, dtype=np.float32)
        cantidad = len(datos) // 784 
        
        # 3. Medición de recursos
        ram_usage = self.process.memory_info().rss / (1024 * 1024)
        cpu_usage = self.process.cpu_percent(interval=None)
        
        end_proc = time.perf_counter()
        t_proc_ms = (end_proc - start_proc) * 1000
        
        print(f"gRPC: Procesadas {cantidad} img. RAM: {ram_usage:.2f}MB, CPU: {cpu_usage}%, T_proc: {t_proc_ms:.2f}ms")
        
        # Retornamos incluyendo el t_proc_ms
        return mnist_pb2.BatchResponse(
            batch_id=request.batch_id,
            images_processed=int(cantidad),
            status="OK",
            ram_usage=float(ram_usage),
            cpu_usage=float(cpu_usage),
            t_proc_ms=float(t_proc_ms)
        )

def serve():
    # Definimos el límite (ej. 200 MB para ir sobrados)
    MAX_MESSAGE_LENGTH = 200 * 1024 * 1024 

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
            ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH)
        ]
    )
    mnist_pb2_grpc.add_MnistServiceServicer_to_server(MnistServicer(), server)
    server.add_insecure_port('[::]:8000') # Puerto definido en el Quadlet
    print("Servidor gRPC iniciado (Límite 200MB) en puerto 8000...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()