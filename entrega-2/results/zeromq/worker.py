import zmq
import psutil
import os
import numpy as np
import mnist_pb2 # Reutilizamos tu contrato Protobuf

def serve():
    context = zmq.Context()
    # Socket para responder (REPLY)
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:8000") # Puerto definido en tu infraestructura
    
    process = psutil.Process(os.getpid())
    print("Worker ZeroMQ listo en puerto 8000...")

    while True:
        # Recibir mensaje (bytes de Protobuf)
        message_bytes = socket.recv()
        
        # Deserializar usando el contrato que ya tienes
        request = mnist_pb2.BatchRequest()
        request.ParseFromString(message_bytes)
        
        # Procesamiento
        psutil.cpu_percent(interval=None)
        datos = np.frombuffer(request.image_data, dtype=np.float32)
        cantidad = len(datos) // 784
        
        # Métricas
        ram_usage = process.memory_info().rss / (1024 * 1024)
        cpu_usage = psutil.cpu_percent(interval=None)
        
        # Preparar respuesta Protobuf
        response = mnist_pb2.BatchResponse(
            batch_id=request.batch_id,
            images_processed=int(cantidad),
            status="OK",
            ram_usage=float(ram_usage),
            cpu_usage=float(cpu_usage)
        )
        
        # Enviar respuesta como bytes
        # Enviar respuesta como bytes
        socket.send(response.SerializeToString())
        
        # --- LOG COMPLETO PARA SYSTEMD ---
        print(f"ZMQ: Procesadas {int(cantidad)} imágenes. RAM: {ram_usage:.2f}MB, CPU: {cpu_usage}%")

if __name__ == "__main__":
    serve()