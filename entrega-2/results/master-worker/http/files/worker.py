from fastapi import FastAPI, Request
import uvicorn
import psutil
import os

app = FastAPI()
process = psutil.Process(os.getpid())

@app.post("/procesar")
async def procesar_datos(request: Request):
    payload = await request.json()
    imagenes = payload.get("imagenes", [])
    
    # Tarea de cómputo
    cantidad = len(imagenes)
    
    # Medición de recursos internos
    ram_usage = process.memory_info().rss / (1024 * 1024)  # MB
    cpu_usage = psutil.cpu_percent(interval=None)         # %
    
    print(f"Procesadas {cantidad} imágenes. RAM: {ram_usage:.2f}MB, CPU: {cpu_usage}%")
    
    return {
        "worker_ip": request.client.host,
        "imagenes_contadas": cantidad,
        "ram_mb": ram_usage,
        "cpu_percent": cpu_usage
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)