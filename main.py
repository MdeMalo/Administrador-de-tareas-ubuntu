import tkinter as tk
import psutil
from ui import ProcessMonitorUI
from process_manager import ProcessManager

class ProcessMonitorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.process_manager = ProcessManager()
        self.ui = ProcessMonitorUI(
            self.root,
            on_select_callback=self._on_select,
            on_finalize_callback=self._on_finalize,
            on_search_callback=self._on_search
        )
        self._schedule_update()

    def _on_select(self, pid):
        self.process_manager.pid_seleccionado = pid

    def _on_finalize(self):
        pid = self.process_manager.pid_seleccionado
        if pid is None:
            self.ui.show_warning("Advertencia", "Por favor, selecciona un proceso primero.")
            return

        # Obtener el nombre del proceso para la confirmación
        try:
            proceso = psutil.Process(pid)
            nombre_proceso = proceso.name()
        except psutil.NoSuchProcess:
            self.ui.show_error("Error", f"El proceso con PID {pid} ya no existe.")
            self.process_manager.pid_seleccionado = None
            return

        # Mostrar diálogo de confirmación
        if not self.ui.ask_yes_no("Confirmar", f"¿Finalizar el proceso '{nombre_proceso}' (PID {pid})?"):
            return

        # Finalizar el proceso
        success, message, message_type = self.process_manager.finalize_process(pid, nombre_proceso)
        if success:
            self.ui.show_info(message_type, message)
            self.process_manager.pid_seleccionado = None
        else:
            self.ui.show_error(message_type, message)

        # Actualizar la tabla inmediatamente
        self._update_table()

    def _on_search(self):
        self._update_table()

    def _update_table(self):
        search_text = self.ui.get_search_text()
        procesos = self.process_manager.get_processes(search_text)
        self.ui.update_table(procesos, self.process_manager.pid_seleccionado)

    def _schedule_update(self):
        self._update_table()
        self.root.after(1000, self._schedule_update)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ProcessMonitorApp()
    app.run()