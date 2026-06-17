# Entrenamiento de un modelo IA con framework PyTorch 

## url: https://pythonguides.com/pytorch-mnist/


### 1. Crear el entorno virtual

Ejecuta este comando para crear la carpeta llamada `.venv`:

```bash
python3 -m venv .venv
```

*(Si usas Windows, a veces basta con `python -m venv .venv`)*.

### 2. Activarlo (Paso crucial)

Una vez creado, **tienes que activarlo** para que tu terminal "sepa" que debe usar ese entorno y no el de tu sistema operativo:

* **En Linux o macOS:**
```bash
source .venv/bin/activate
```

* **En Windows:**
```bash
.venv\Scripts\activate
```

### 3. ¿Cómo saber si funcionó?

Una vez activado, verás que en tu terminal aparece `(.venv)` al principio de la línea de comandos (a la izquierda).

Ahora, cuando instales algo, **hazlo siempre dentro de este entorno**:

```bash
pip install torch torchvision matplotlib
```

```bash
cd Setmana5_PyTorch
python interact.py 
```