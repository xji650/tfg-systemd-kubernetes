from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()

@app.post("/procesar")
async def procesar_datos(request: Request):
    # Recibimos el JSON gigante del Nodo Pare
    payload = await request.json()
    imagenes = payload.get("imagenes", [])
    
    # La Tarea: Contar
    cantidad = len(imagenes)
    print(f"He recibido y contado {cantidad} imágenes.")
    
    # Devolver el resultado
    return {"worker_ip": request.client.host, "imagenes_contadas": cantidad}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)