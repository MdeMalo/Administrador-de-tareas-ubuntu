import tkinter as tk
from tkinter import ttk, messagebox
import psutil

# Variable para almacenar el PID del proceso seleccionado
pid_seleccionado = None

def actualizar_tabla():
    global pid_seleccionado

    # Guardar el estado del ordenamiento y posición del scroll
    columna_ordenada = tabla.sort_column
    reverso = tabla.sort_reverse
    posicion_scroll = tabla.yview()

    # Guardar el texto de búsqueda actual
    texto_busqueda = entrada_busqueda.get().lower()

    # Limpiar la tabla
    for fila in tabla.get_children():
        tabla.delete(fila)

    # Actualizar los datos de los procesos
    try:
        procesos = psutil.process_iter(['pid', 'name', 'cpu_percent'])
        nuevo_iid_seleccionado = None
        for proceso in procesos:
            nombre_proceso = proceso.info['name'].lower()
            # Mostrar solo procesos que coincidan con el texto de búsqueda
            if texto_busqueda in nombre_proceso or not texto_busqueda:
                iid = tabla.insert("", "end", values=(proceso.info['pid'], proceso.info['name'], proceso.info['cpu_percent']))
                # Restaurar la selección si el PID coincide
                if pid_seleccionado is not None and proceso.info['pid'] == pid_seleccionado:
                    nuevo_iid_seleccionado = iid

        # Aplicar la selección si se encontró el PID
        if nuevo_iid_seleccionado:
            tabla.selection_set(nuevo_iid_seleccionado)
        else:
            # Si el proceso ya no existe o no coincide con el filtro, limpiar la selección
            pid_seleccionado = None
            tabla.selection_remove(tabla.selection())

    except psutil.AccessDenied:
        pass

    # Restaurar la posición del scroll
    tabla.yview_moveto(posicion_scroll[0])

    # Restaurar el ordenamiento si existe
    if columna_ordenada:
        ordenar_por_columna(columna_ordenada, reverso, actualizar_seleccion=False)

    # Programar la próxima actualización
    root.after(1000, actualizar_tabla)

def ordenar_por_columna(columna, reverso, actualizar_seleccion=True):
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

    # Actualizar el comando del encabezado
    tabla.heading(columna, command=lambda: ordenar_por_columna(columna, not reverso))

def registrar_seleccion(event):
    global pid_seleccionado
    seleccion = tabla.selection()
    if seleccion:
        item = tabla.item(seleccion[0])
        valores = item['values']
        pid_seleccionado = valores[0]  # Guardar el PID del proceso seleccionado
    else:
        pid_seleccionado = None  # Limpiar la selección si no hay nada seleccionado

def finalizar_proceso():
    global pid_seleccionado
    if pid_seleccionado is None:
        messagebox.showwarning("Advertencia", "Por favor, selecciona un proceso primero.")
        return

    # Obtener el nombre del proceso para la confirmación
    try:
        proceso = psutil.Process(pid_seleccionado)
        nombre_proceso = proceso.name()
    except psutil.NoSuchProcess:
        messagebox.showerror("Error", f"El proceso con PID {pid_seleccionado} ya no existe.")
        pid_seleccionado = None
        tabla.selection_remove(tabla.selection())
        return

    # Mostrar diálogo de confirmación
    if not messagebox.askyesno("Confirmar", f"¿Finalizar el proceso '{nombre_proceso}' (PID {pid_seleccionado})?"):
        return

    # Intentar terminar el proceso
    try:
        proceso = psutil.Process(pid_seleccionado)
        proceso.terminate()  # Enviar señal de terminación (SIGTERM en Unix, terminate en Windows)
        messagebox.showinfo("Éxito", f"Proceso '{nombre_proceso}' (PID {pid_seleccionado}) terminado.")
        pid_seleccionado = None  # Limpiar la selección
        tabla.selection_remove(tabla.selection())  # Limpiar la selección en la tabla
    except psutil.NoSuchProcess:
        messagebox.showerror("Error", f"El proceso con PID {pid_seleccionado} ya no existe.")
        pid_seleccionado = None
        tabla.selection_remove(tabla.selection())
    except psutil.AccessDenied:
        messagebox.showerror("Error", f"No tienes permisos para finalizar el proceso '{nombre_proceso}'.")
    except Exception as e:
        messagebox.showerror("Error", f"Error al intentar finalizar el proceso: {str(e)}")

def filtrar_procesos(event):
    # Forzar una actualización de la tabla para aplicar el filtro
    actualizar_tabla()

# Crear la ventana principal
root = tk.Tk()
root.title("Administrador de Tareas Básico")
root.geometry("800x600")

# Crear un marco para la búsqueda
frame_busqueda = ttk.Frame(root)
frame_busqueda.pack(fill=tk.X, padx=5, pady=5)

# Etiqueta y campo de búsqueda
ttk.Label(frame_busqueda, text="Buscar proceso:").pack(side=tk.LEFT)
entrada_busqueda = ttk.Entry(frame_busqueda)
entrada_busqueda.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
entrada_busqueda.bind("<KeyRelease>", filtrar_procesos)

# Crear un marco para la tabla
frame_tabla = ttk.Frame(root)
frame_tabla.pack(fill=tk.BOTH, expand=True)

# Crear la tabla
tabla = ttk.Treeview(frame_tabla, columns=("PID", "Nombre", "CPU (%)"), show="headings")
tabla.heading("PID", text="PID", command=lambda: ordenar_por_columna("PID", False))
tabla.heading("Nombre", text="Nombre", command=lambda: ordenar_por_columna("Nombre", False))
tabla.heading("CPU (%)", text="CPU (%)", command=lambda: ordenar_por_columna("CPU (%)", False))

# Ajustar el ancho y alineación de las columnas
tabla.column("PID", width=100, anchor="center")
tabla.column("Nombre", width=300, anchor="w")
tabla.column("CPU (%)", width=150, anchor="center")

# Agregar barra de desplazamiento
scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=tabla.yview)
tabla.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
tabla.pack(fill=tk.BOTH, expand=True)

# Vincular la selección de filas
tabla.bind("<<TreeviewSelect>>", registrar_seleccion)

# Crear un marco para los botones
frame_botones = ttk.Frame(root)
frame_botones.pack(fill=tk.X, padx=5, pady=5)

# Botón para finalizar proceso
btn_finalizar = ttk.Button(frame_botones, text="Finalizar Proceso", command=finalizar_proceso)
btn_finalizar.pack(side=tk.LEFT)

# Inicializar variables para el ordenamiento
tabla.sort_column = None
tabla.sort_reverse = False

# Iniciar la actualización de la tabla
actualizar_tabla()

root.mainloop()