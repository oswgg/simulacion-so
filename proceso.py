import random

class Process:

    # Contador estático para IDs únicos
    _id_counter = 0
    
    # Estados posibles de un proceso según especificación
    READY = "Listo"           # En cola de listos, esperando CPU
    RUNNING = "Ejecutando"    # Usando CPU
    WAITING = "Esperando"     # Bloqueado esperando recurso
    TERMINATED = "Terminado"  # Proceso finalizado
    
    def __init__(self, name, burst_time, priority=None, memory_required=100):
        Process._id_counter += 1
        self.pid = Process._id_counter
        self.name = name
        self.burst_time = burst_time           # Tiempo total de CPU necesario
        self.remaining_time = burst_time       # Tiempo restante de CPU
        self.priority = priority if priority else random.randint(1, 10)
        self.memory_required = memory_required # Memoria en MB
        
        # Estado del proceso
        self.state = Process.READY
        
        # Recursos asignados
        self.assigned_cpu = False
        self.assigned_memory = 0
        
        # Estadísticas
        self.arrival_time = 0      # Cuándo llegó al sistema
        self.start_time = None     # Cuándo empezó a ejecutarse por primera vez
        self.finish_time = None    # Cuándo terminó
        self.waiting_time = 0      # Tiempo total esperando
        self.turnaround_time = 0   # Tiempo total en el sistema
        self.response_time = None  # Tiempo desde llegada hasta primera ejecución
        
        # Para Round Robin
        self.time_quantum_used = 0  # Tiempo usado del quantum actual
    
    def set_state(self, new_state):

        old_state = self.state
        self.state = new_state
        return old_state
    
    def assign_cpu(self):

        self.assigned_cpu = True
        old_state = self.set_state(Process.RUNNING)
        
        # Si es la primera vez que ejecuta, registrar tiempo de respuesta
        if self.start_time is None:
            self.start_time = 0  # Se actualizará con el tiempo real
    
    def release_cpu(self):

        self.assigned_cpu = False
        if self.remaining_time > 0:
            self.set_state(Process.READY)
        else:
            self.set_state(Process.TERMINATED)
    
    def execute(self, time_slice):

        if self.state != Process.RUNNING:
            return False
        
        # Ejecutar por el tiempo dado
        execution_time = min(time_slice, self.remaining_time)
        self.remaining_time -= execution_time
        self.time_quantum_used += execution_time
        
        # Verificar si terminó
        if self.remaining_time <= 0:
            self.remaining_time = 0
            self.set_state(Process.TERMINATED)
            return True
        
        return False
    
    def is_finished(self):

        return self.remaining_time <= 0 or self.state == Process.TERMINATED
    
    def assign_memory(self, amount):

        self.assigned_memory = amount
    
    def release_memory(self):

        self.assigned_memory = 0
    
    def calculate_statistics(self, current_time):

        if self.state == Process.TERMINATED and self.finish_time is None:
            self.finish_time = current_time
            self.turnaround_time = self.finish_time - self.arrival_time
            
            # Waiting time = Turnaround time - Burst time
            self.waiting_time = self.turnaround_time - self.burst_time
            
            # Response time (si no se calculó antes)
            if self.response_time is None and self.start_time is not None:
                self.response_time = self.start_time - self.arrival_time
    
    def reset_quantum(self):

        self.time_quantum_used = 0
    
    def get_progress_percentage(self):

        if self.burst_time == 0:
            return 100.0
        return ((self.burst_time - self.remaining_time) / self.burst_time) * 100
    
    def __str__(self):


        return f"P{self.pid}({self.name})"
    
    def __repr__(self):
        return self.__str__()
    
    def __lt__(self, other):

        return self.priority < other.priority
    
    def get_info(self):

        return {
            'PID': self.pid,
            'Nombre': self.name,
            'Estado': self.state,
            'Prioridad': self.priority,
            'Burst Time': f"{self.burst_time} ms",
            'Tiempo Restante': f"{self.remaining_time} ms",
            'Memoria': f"{self.memory_required} MB",
            'Progreso': f"{self.get_progress_percentage():.1f}%",
            'Tiempo Espera': f"{self.waiting_time} ms",
            'Turnaround': f"{self.turnaround_time} ms"
        }
    
    def get_pcb_summary(self):

        return (f"PID: {self.pid} | Estado: {self.state} | "
                f"Prioridad: {self.priority} | "
                f"Burst: {self.burst_time}ms | "
                f"Restante: {self.remaining_time}ms | "
                f"CPU: {'Sí' if self.assigned_cpu else 'No'} | "
                f"Memoria: {self.assigned_memory}MB")
    
    @staticmethod
    def reset_counter():

        Process._id_counter = 0
