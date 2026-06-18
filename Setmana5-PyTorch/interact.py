import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image, ImageDraw
import tkinter as tk
from tkinter import Canvas

# --- 1. DEFINIR LA ARQUITECTURA ---
class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, stride=1, padding=1)
        self.relu = nn.ReLU()
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.conv1(x)
        x = self.relu(x)
        x = self.pool(x)
        x = self.conv2(x)
        x = self.relu(x)
        x = self.pool(x)
        x = x.view(-1, 64 * 7 * 7)
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x

# --- 2. CARGAR EL MODELO ---
model = CNN()
model.load_state_dict(torch.load('best_model.pth', map_location='cpu'))
model.eval()

# --- 3. PREPROCESADO ---
transform = transforms.Compose([
    transforms.Resize((28, 28)),
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])

# --- NUEVO: CREAR IMAGEN OCULTA EN MEMORIA ---
# Creamos una imagen negra de 200x200 píxeles
img_memory = Image.new('L', (200, 200), color='black')
draw = ImageDraw.Draw(img_memory)

# --- 4. LÓGICA DE INFERENCIA Y UI ---
def paint(event):
    # Grosor del pincel
    x1, y1 = (event.x - 8), (event.y - 8)
    x2, y2 = (event.x + 8), (event.y + 8)
    
    # 1. Pintar en la pantalla (Tkinter)
    canvas.create_oval(x1, y1, x2, y2, fill='white', outline='white')
    # 2. Pintar en nuestra imagen oculta (PIL) simultáneamente
    draw.ellipse([x1, y1, x2, y2], fill='white')

def classify():
    # Ahora usamos la imagen en memoria directamente (ya no hay que invertir ni usar postscript)
    input_tensor = transform(img_memory).unsqueeze(0)
    
    with torch.no_grad():
        output = model(input_tensor)
        probabilities = torch.nn.functional.softmax(output, dim=1)[0]
        pred = torch.argmax(probabilities).item()
        confidence = probabilities[pred].item() * 100
        
    result_label.config(text=f"Predicción: {pred} (Seguridad: {confidence:.2f}%)")

def clear_canvas():
    # Limpiamos la pantalla
    canvas.delete("all")
    # Limpiamos la imagen en memoria pintándola toda de negro de nuevo
    draw.rectangle((0, 0, 200, 200), fill="black")
    result_label.config(text="Dibuja un número")

# Configurar la ventana
root = tk.Tk()
root.title("Clasificador MNIST - TFG")

canvas = Canvas(root, width=200, height=200, bg='black')
canvas.pack(pady=10)

# Al arrastrar el ratón, llamamos a la función paint
canvas.bind('<B1-Motion>', paint)

# Botones
btn_frame = tk.Frame(root)
btn_frame.pack()

btn_classify = tk.Button(btn_frame, text="Clasificar", command=classify)
btn_classify.pack(side=tk.LEFT, padx=5)

btn_clear = tk.Button(btn_frame, text="Limpiar", command=clear_canvas)
btn_clear.pack(side=tk.LEFT, padx=5)

result_label = tk.Label(root, text="Dibuja un número", font=('Helvetica', 14))
result_label.pack(pady=10)

root.mainloop()