from fastapi import FastAPI, Request
import uvicorn
import psutil
import os
import time

app = FastAPI()
process = psutil.Process(os.getpid())

# Inicialización obligatoria para psutil
process.cpu_percent(interval=None)

@app.post("/procesar")
async def procesar_datos(request: Request):
    # 1. Limpieza de buffer de CPU (lanzamos una medida vacía)
    process.cpu_percent(interval=None)
    
    start_proc = time.perf_counter()
    
    # 2. Deserialización
    payload = await request.json()
    imagenes = payload.get("imagenes", [])
    
    # 3. Medición de recursos
    # Usamos rss para memoria residente (RAM real usada)
    ram_mb = process.memory_info().rss / (1024 * 1024)
    
    # Medición de CPU desde la limpieza inicial hasta ahora
    cpu_usage = process.cpu_percent(interval=None)
    
    end_proc = time.perf_counter()
    t_proc_ms = (end_proc - start_proc) * 1000
    
    # Print de control para depurar en el nodo
    print(f"RAM: {ram_mb:.2f} MB, CPU: {cpu_usage}%, T_proc: {t_proc_ms:.2f} ms")

    return {
        "batch_id": payload.get("batch_id", "N/A"),
        "images_processed": len(imagenes),
        "status": "OK",
        "ram_usage": float(ram_mb),
        "cpu_usage": float(cpu_usage),
        "t_proc_ms": float(t_proc_ms)
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)