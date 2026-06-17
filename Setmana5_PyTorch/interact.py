import torch
import torchvision.transforms as transforms
from PIL import Image
import tkinter as tk
from tkinter import Canvas
import io

# Definimos la clase CNN igual que en tu notebook
class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        # ... (debe ser la misma estructura exacta que usaste para entrenar) ...

# Cargar el modelo
model = CNN()
model.load_state_dict(torch.load('best_model.pth', map_location='cpu'))
model.eval()

transform = transforms.Compose([
    transforms.Resize((28, 28)),
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])

def classify():
    # Capturar el canvas y convertirlo a imagen
    canvas.postscript(file='temp.eps', colormode='color')
    img = Image.open('temp.eps').convert('L').resize((28, 28))
    
    # Invertir colores (el modelo espera fondo negro/número blanco)
    img = ImageOps.invert(img)
    
    input_tensor = transform(img).unsqueeze(0)
    with torch.no_grad():
        pred = model(input_tensor).argmax(dim=1).item()
    result_label.config(text=f"Predicción: {pred}")

# Configurar la ventana
root = tk.Tk()
canvas = Canvas(root, width=200, height=200, bg='black')
canvas.pack()
canvas.bind('<B1-Motion>', lambda e: canvas.create_oval(e.x, e.y, e.x+10, e.y+10, fill='white'))

btn = tk.Button(root, text="Clasificar", command=classify)
btn.pack()
result_label = tk.Label(root, text="Dibuja un número")
result_label.pack()

root.mainloop()