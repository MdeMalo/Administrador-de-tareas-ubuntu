import tkinter as tk
from tkinter import ttk, messagebox

class ProcessMonitorUI:
    def __init__(self, root, on_select_callback, on_finalize_callback, on_search_callback):
        self.root = root
        self.root.title("Administrador de Tareas")
        self.root.geometry("800x600")
        
        self.on_select_callback = on_select_callback
        self.on_finalize_callback = on_finalize_callback
        self.on_search_callback = on_search_callback
        
        self.pid_seleccionado = None
        self.sort_column = None
        self.sort_reverse = False
        
        self._setup_ui()

    def _setup_ui(self):
        # Marco para la búsqueda
        frame_busqueda = ttk.Frame(self.root)
        frame_busqueda.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(frame_busqueda, text="Buscar proceso:").pack(side=tk.LEFT)
        self.entrada_busqueda = ttk.Entry(frame_busqueda)
        self.entrada_busqueda.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.entrada_busqueda.bind("<KeyRelease>", self._on_search)

        # Marco para la tabla
        frame_tabla = ttk.Frame(self.root)
        frame_tabla.pack(fill=tk.BOTH, expand=True)

        # Crear la tabla
        self.tabla = ttk.Treeview(frame_tabla, columns=("PID", "Nombre", "CPU (%)"), show="headings")
        self.tabla.heading("PID", text="PID", command=lambda: self._sort_column("PID"))
        self.tabla.heading("Nombre", text="Nombre", command=lambda: self._sort_column("Nombre"))
        self.tabla.heading("CPU (%)", text="CPU (%)", command=lambda: self._sort_column("CPU (%)"))

        # Ajustar el ancho y alineación de las columnas
        self.tabla.column("PID", width=100, anchor="center")
        self.tabla.column("Nombre", width=300, anchor="w")
        self.tabla.column("CPU (%)", width=150, anchor="center")

        # Barra de desplazamiento
        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tabla.pack(fill=tk.BOTH, expand=True)

        # Vincular la selección de filas
        self.tabla.bind("<<TreeviewSelect>>", self._on_select)

        # Marco para los botones
        frame_botones = ttk.Frame(self.root)
        frame_botones.pack(fill=tk.X, padx=5, pady=5)
        btn_finalizar = ttk.Button(frame_botones, text="Finalizar Proceso", command=self._on_finalize)
        btn_finalizar.pack(side=tk.LEFT)

    def _on_select(self, event):
        seleccion = self.tabla.selection()
        if seleccion:
            item = self.tabla.item(seleccion[0])
            valores = item['values']
            self.pid_seleccionado = valores[0]
        else:
            self.pid_seleccionado = None
        self.on_select_callback(self.pid_seleccionado)

    def _on_finalize(self):
        self.on_finalize_callback()
        
    def _on_search(self, event):
        self.on_search_callback()

    def _sort_column(self, columna):
        if self.sort_column == columna:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = columna
            self.sort_reverse = False

    def update_table(self, procesos, pid_seleccionado):
        # Guardar la posición del scroll
        posicion_scroll = self.tabla.yview()

        # Limpiar la tabla
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        # Insertar procesos
        nuevo_iid_seleccionado = None
        for proceso in procesos:
            iid = self.tabla.insert("", "end", values=(proceso['pid'], proceso['name'], proceso['cpu_percent']))
            if pid_seleccionado is not None and proceso['pid'] == pid_seleccionado:
                nuevo_iid_seleccionado = iid

        # Restaurar la selección
        if nuevo_iid_seleccionado:
            self.tabla.selection_set(nuevo_iid_seleccionado)
        else:
            self.tabla.selection_remove(self.tabla.selection())

        # Restaurar la posición del scroll
        self.tabla.yview_moveto(posicion_scroll[0])

        # Aplicar ordenamiento si existe
        if self.sort_column:
            datos = [(self.tabla.set(fila, self.sort_column), fila) for fila in self.tabla.get_children('')]
            try:
                if self.sort_column == "PID":
                    datos.sort(reverse=self.sort_reverse, key=lambda x: int(x[0]))
                elif self.sort_column == "Nombre":
                    datos.sort(reverse=self.sort_reverse)
                elif self.sort_column == "CPU (%)":
                    datos.sort(reverse=self.sort_reverse, key=lambda x: float(x[0]) if x[0].replace('.', '', 1).isdigit() else 0)
            except ValueError:
                pass

            for index, (_, fila) in enumerate(datos):
                self.tabla.move(fila, '', index)

    def get_search_text(self):
        return self.entrada_busqueda.get().lower()

    def show_warning(self, title, message):
        messagebox.showwarning(title, message)

    def show_error(self, title, message):
        messagebox.showerror(title, message)

    def show_info(self, title, message):
        messagebox.showinfo(title, message)

    def ask_yes_no(self, title, message):
        return messagebox.askyesno(title, message)