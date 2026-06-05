from fastapi import FastAPI, Request
import uvicorn
import psutil
import os
import time

app = FastAPI()
process = psutil.Process(os.getpid())

# Inicializamos la CPU al arrancar para tener una línea base del 0%
process.cpu_percent(interval=None)

@app.post("/procesar")
async def procesar_datos(request: Request):
    # 1. Inicio del cronómetro T_proc
    start_proc = time.time()
    
    # 2. Deserialización (Aquí ocurre el pico de memoria para JSON)
    payload = await request.json()
    imagenes = payload.get("imagenes", [])
    
    # Tarea de cómputo
    cantidad = len(imagenes)
    
    # 3. Medición del PICO de RAM (justo cuando el JSON está cargado entero en memoria)
    ram_mb = process.memory_info().rss / (1024 * 1024)  
    
    # 4. Medición del promedio de CPU (desde que llegó la petición hasta ahora)
    cpu_usage = process.cpu_percent(interval=None)         
    
    # 5. Fin del cronómetro T_proc
    end_proc = time.time()
    t_proc_ms = (end_proc - start_proc) * 1000
    
    print(f"Procesadas {cantidad} img. RAM: {ram_mb:.2f}MB, CPU: {cpu_usage}%, T_proc: {t_proc_ms:.2f}ms")
    
    return {
        "worker_ip": request.client.host,
        "imagenes_contadas": cantidad,
        "ram_max_mb": ram_mb,
        "cpu_promedio": cpu_usage,
        "t_proc_ms": t_proc_ms
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)