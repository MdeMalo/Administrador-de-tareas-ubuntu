import tkinter as tk
from tkinter import ttk
import psutil

def actualizar_tabla():
    # Guardar el estado del ordenamiento
    columna_ordenada = tabla.sort_column
    reverso = tabla.sort_reverse

    # Guardar la posición del scroll
    posicion_scroll = tabla.yview()

    # Limpiar y actualizar los datos de la tabla
    for fila in tabla.get_children():
        tabla.delete(fila)
    procesos = psutil.process_iter(['pid', 'name', 'cpu_percent'])
    for proceso in procesos:
        tabla.insert("", "end", values=(proceso.info['pid'], proceso.info['name'], proceso.info['cpu_percent']))

    # Restaurar la posición del scroll
    tabla.yview_moveto(posicion_scroll[0])

    # Restaurar el ordenamiento si existe
    if columna_ordenada:
        ordenar_por_columna(columna_ordenada, reverso)

    # Programar la próxima actualización
    root.after(1000, actualizar_tabla)

def ordenar_por_columna(columna, reverso):
    # Obtener los datos según el tipo de columna
    if columna == "PID":
        datos = [(int(tabla.set(fila, columna)), fila) for fila in tabla.get_children('')]
    elif columna == "Nombre":
        datos = [(tabla.set(fila, columna), fila) for fila in tabla.get_children('')]
    elif columna == "CPU (%)":
        datos = [(float(tabla.set(fila, columna)) if tabla.set(fila, columna).replace('.', '', 1).isdigit() else 0, fila) 
                 for fila in tabla.get_children('')]

    # Ordenar los datos
    datos.sort(reverse=reverso)

    # Reorganizar las filas en la tabla
    for index, (_, fila) in enumerate(datos):
        tabla.move(fila, '', index)

    # Actualizar el estado del ordenamiento
    tabla.sort_column = columna
    tabla.sort_reverse = reverso

    # Actualizar el comando del encabezado para alternar la dirección
    tabla.heading(columna, command=lambda: ordenar_por_columna(columna, not reverso))

# Crear la ventana principal
root = tk.Tk()
root.title("Monitor de Procesos en Tabla")
root.geometry("800x600")

# Crear la tabla
tabla = ttk.Treeview(root, columns=("PID", "Nombre", "CPU (%)"), show="headings")
tabla.heading("PID", text="PID", command=lambda: ordenar_por_columna("PID", False))
tabla.heading("Nombre", text="Nombre", command=lambda: ordenar_por_columna("Nombre", False))
tabla.heading("CPU (%)", text="CPU (%)", command=lambda: ordenar_por_columna("CPU (%)", False))

# Ajustar el ancho y alineación de las columnas
tabla.column("PID", width=100, anchor="center")
tabla.column("Nombre", width=300, anchor="w")
tabla.column("CPU (%)", width=150, anchor="center")

# Agregar barra de desplazamiento
scrollbar = ttk.Scrollbar(root, orient="vertical", command=tabla.yview)
tabla.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
tabla.pack(fill=tk.BOTH, expand=True)

# Inicializar variables para el ordenamiento
tabla.sort_column = None
tabla.sort_reverse = False

# Iniciar la actualización de la tabla
actualizar_tabla()

root.mainloop()