import zmq
import psutil
import os
import numpy as np
import time
import msgpack

def serve():
    context = zmq.Context()
    # Socket para responder (REPLY)
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:8000") # Puerto definido en tu infraestructura
    
    process = psutil.Process(os.getpid())
    process.cpu_percent(interval=None) # Inicialización obligatoria
    
    print("Worker ZeroMQ + MessagePack listo en puerto 8000...")

    while True:
        message_bytes = socket.recv()
        
        # 1. Limpieza de buffer de CPU para esta petición
        process.cpu_percent(interval=None)
        start_proc = time.perf_counter()
        
        try:
            # 2. Deserializar con límite de 200MB para evitar cuelgues
            request = msgpack.unpackb(message_bytes, raw=False, max_bin_len=200*1024*1024, max_str_len=200*1024*1024)
            
            # 3. Procesamiento (usamos las llaves del diccionario dinámico)
            datos = np.frombuffer(request['image_data'], dtype=np.float32)
            cantidad = len(datos) // 784
            
            # 4. Métricas
            ram_usage = process.memory_info().rss / (1024 * 1024)
            cpu_usage = process.cpu_percent(interval=None)
            
            end_proc = time.perf_counter()
            t_proc_ms = (end_proc - start_proc) * 1000
            
            # Preparar respuesta como Diccionario Python
            response = {
                'batch_id': request['batch_id'],
                'images_processed': int(cantidad),
                'status': "OK",
                'ram_usage': float(ram_usage),
                'cpu_usage': float(cpu_usage),
                't_proc_ms': float(t_proc_ms)
            }
            
            # Enviar respuesta serializada en bytes
            socket.send(msgpack.packb(response, use_bin_type=True))
            
            print(f"ZMQ+MsgPack: Procesadas {int(cantidad)} img. RAM: {ram_usage:.2f}MB, CPU: {cpu_usage}%, T_proc: {t_proc_ms:.2f}ms")
            
        except Exception as e:
            # Control de errores para no bloquear el Master
            error_msg = f"Error en el worker: {str(e)}"
            print(error_msg)
            response_error = {
                'error': error_msg,
                'status': "ERROR"
            }
            socket.send(msgpack.packb(response_error, use_bin_type=True))

if __name__ == "__main__":
    serve()