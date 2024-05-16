import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import pydicom
from pydicom.pixel_data_handlers.util import apply_voi_lut
from ttkthemes import ThemedStyle


def aplicar_filtro_negativo(imagen):
    # Convertir la imagen a un arreglo numpy
    datos_imagen = np.array(imagen)

    # Aplicar el filtro negativo
    datos_imagen_negativo = 255 - datos_imagen

    # Crear una nueva imagen con los datos modificados
    imagen_negativo = Image.fromarray(datos_imagen_negativo)

    return imagen_negativo


def centrar_imagen(canvas, image):
    # Obtiene las dimensiones del lienzo
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()

    # Obtiene las dimensiones de la imagen
    image_width, image_height = image.size

    # Calcula las coordenadas para centrar la imagen
    x = (canvas_width - image_width) / 2
    y = (canvas_height - image_height) / 2

    return x, y


def cargar_imagen():
    global imagen_original, imagen_negativo
    # Abrir un cuadro de diálogo para seleccionar una imagen
    ruta_imagen = filedialog.askopenfilename(
        filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.dcm")]
    )

    if ruta_imagen:
        if ruta_imagen.lower().endswith(".dcm"):
            # Cargar imagen DICOM
            ds = pydicom.dcmread(ruta_imagen)
            imagen_np = ds.pixel_array
            imagen_original = Image.fromarray(apply_voi_lut(imagen_np, ds))
        else:
            # Cargar imagen común
            imagen_original = Image.open(ruta_imagen)

        imagen_mostrada = imagen_original.copy()
        imagen_mostrada.thumbnail((400, 400))
        img_tk = ImageTk.PhotoImage(imagen_mostrada)
        canvas_original.create_image(
            *centrar_imagen(canvas_original, imagen_mostrada), anchor="nw", image=img_tk
        )
        canvas_original.image = img_tk

        # Aplicar el filtro negativo y mostrar la imagen resultante
        imagen_negativo = aplicar_filtro_negativo(imagen_original)
        imagen_negativo_mostrada = imagen_negativo.copy()
        imagen_negativo_mostrada.thumbnail((400, 400))
        img_negativo_tk = ImageTk.PhotoImage(imagen_negativo_mostrada)
        canvas_negativo.create_image(
            *centrar_imagen(canvas_negativo, imagen_negativo_mostrada),
            anchor="nw",
            image=img_negativo_tk,
        )
        canvas_negativo.image = img_negativo_tk

        # Habilitar el botón de guardar
        btn_guardar.config(state=tk.NORMAL)


def guardar_imagen():
    if imagen_negativo:
        ruta_guardar = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg;*.jpeg"),
                ("All files", "*.*"),
            ],
        )
        if ruta_guardar:
            imagen_negativo.save(ruta_guardar)
            messagebox.showinfo("Guardar Imagen", f"Imagen guardada en: {ruta_guardar}")


# Crear la ventana principal
root = tk.Tk()
root.title("Filtro Negativo de Imágenes")

# Estilo personalizado
style = ThemedStyle(root)
style.set_theme("equilux")

# Crear el marco principal
main_frame = ttk.Frame(root, padding="10 10 10 10")
main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Crear un canvas para mostrar la imagen original
label_original = ttk.Label(
    main_frame, text="Imagen Original", font=("Arial", 12, "bold")
)
label_original.grid(row=0, column=0, padx=10, pady=10)
canvas_original = tk.Canvas(
    main_frame, width=400, height=400, bg="white", borderwidth=2, relief="sunken"
)
canvas_original.grid(row=1, column=0, padx=10, pady=10)

# Crear un canvas para mostrar la imagen con el filtro negativo
label_negativo = ttk.Label(
    main_frame, text="Imagen con Filtro Negativo", font=("Arial", 12, "bold")
)
label_negativo.grid(row=0, column=1, padx=10, pady=10)
canvas_negativo = tk.Canvas(
    main_frame, width=400, height=400, bg="white", borderwidth=2, relief="sunken"
)
canvas_negativo.grid(row=1, column=1, padx=10, pady=10)

# Botón para cargar la imagen
btn_cargar = ttk.Button(main_frame, text="Cargar Imagen", command=cargar_imagen)
btn_cargar.grid(row=2, column=0, columnspan=2, pady=10)

# Botón para guardar la imagen
btn_guardar = ttk.Button(
    main_frame, text="Guardar Imagen", command=guardar_imagen, state=tk.DISABLED
)
btn_guardar.grid(row=3, column=0, columnspan=2, pady=10)

# Variables globales para las imágenes
imagen_original = None
imagen_negativo = None

# Iniciar el bucle principal de la interfaz
root.mainloop()
