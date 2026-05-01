import grpc
from concurrent import futures
import psutil
import os
import numpy as np
import mnist_pb2
import mnist_pb2_grpc

class MnistServicer(mnist_pb2_grpc.MnistServiceServicer):
    def __init__(self):
        self.process = psutil.Process(os.getpid())

    # 1. El nombre del método debe ser ProcessBatch (como en el .proto)
    def ProcessBatch(self, request, context):
        psutil.cpu_percent(interval=None)
        
        # 2. El campo se llama image_data, no imagenes_bytes
        datos = np.frombuffer(request.image_data, dtype=np.float32)
        cantidad = len(datos) // 784 
        
        ram_usage = self.process.memory_info().rss / (1024 * 1024)
        cpu_usage = psutil.cpu_percent(interval=None)
        
        print(f"gRPC: Procesadas {cantidad} imágenes. RAM: {ram_usage:.2f}MB, CPU: {cpu_usage}%")
        
        # 3. La clase es BatchResponse y los campos deben coincidir con el .proto
        return mnist_pb2.BatchResponse(
            batch_id=request.batch_id,
            images_processed=int(cantidad),
            status="OK",
            ram_usage=float(ram_usage),
            cpu_usage=float(cpu_usage)
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