import psutil

class ProcessManager:
    def __init__(self):
        self.pid_seleccionado = None

    def get_processes(self, search_text=""):
        procesos = []
        try:
            for proceso in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                nombre_proceso = proceso.info['name'].lower()
                if not search_text or search_text in nombre_proceso:
                    procesos.append({
                        'pid': proceso.info['pid'],
                        'name': proceso.info['name'],
                        'cpu_percent': proceso.info['cpu_percent']
                    })
        except psutil.AccessDenied:
            pass
        return procesos

    def finalize_process(self, pid, nombre_proceso=None):
        if pid is None:
            return False, "Por favor, selecciona un proceso primero.", "Advertencia"
        
        try:
            proceso = psutil.Process(pid)
            if nombre_proceso is None:
                nombre_proceso = proceso.name()
            proceso.terminate()
            return True, f"Proceso '{nombre_proceso}' (PID {pid}) terminado.", "Éxito"
        except psutil.NoSuchProcess:
            return False, f"El proceso con PID {pid} ya no existe.", "Error"
        except psutil.AccessDenied:
            return False, f"No tienes permisos para finalizar el proceso '{nombre_proceso}'.", "Error"
        except Exception as e:
            return False, f"Error al intentar finalizar el proceso: {str(e)}", "Error"