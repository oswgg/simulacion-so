class ResourceManager:

    def __init__(self, num_cpus=1, total_memory=4096):

        self.num_cpus = num_cpus
        self.total_memory = total_memory
        self.available_memory = total_memory

        # Recursos asignados
        self.cpu_in_use = 0
        self.memory_allocations = {}  # {pid: memory_allocated}

        # Log de eventos
        self.event_log = []

    def request_cpu(self, process):

        if self.cpu_in_use >= self.num_cpus:
            msg = f"CPU no disponible para {process}"
            self._log_event(msg, "WARNING")
            return (False, msg)

        # Asignar CPU
        self.cpu_in_use += 1
        msg = f"CPU asignada a {process}"
        self._log_event(msg, "INFO")

        return (True, msg)

    def release_cpu(self, process):

        if self.cpu_in_use > 0:
            self.cpu_in_use -= 1
            msg = f"CPU liberada por {process}"
            self._log_event(msg, "INFO")
            return (True, msg)

        return (False, "No hay CPU en uso")

    def request_memory(self, process):

        required = process.memory_required

        if required > self.available_memory:
            msg = f"Memoria insuficiente para {process} (requiere {required}MB, disponible {self.available_memory}MB)"
            self._log_event(msg, "ERROR")
            return (False, msg)

        # Asignar memoria
        self.available_memory -= required
        self.memory_allocations[process.pid] = required
        process.assign_memory(required)

        msg = f"Memoria asignada a {process}: {required}MB"
        self._log_event(msg, "INFO")

        return (True, msg)

    def release_memory(self, process):

        if process.pid not in self.memory_allocations:
            return (False, f"Proceso {process} no tiene memoria asignada")

        # Liberar memoria
        freed_memory = self.memory_allocations[process.pid]
        self.available_memory += freed_memory
        del self.memory_allocations[process.pid]
        process.release_memory()

        msg = f"Memoria liberada por {process}: {freed_memory}MB"
        self._log_event(msg, "INFO")

        return (True, msg)

    def request_resources(self, process):

        # Intentar asignar memoria primero
        success_mem, msg_mem = self.request_memory(process)

        if not success_mem:
            return (False, msg_mem)

        return (True, f"Recursos asignados a {process}")

    def release_resources(self, process):

        # Liberar memoria
        if process.pid in self.memory_allocations:
            self.release_memory(process)

    def has_available_resources(self, process):

        return process.memory_required <= self.available_memory

    def get_memory_usage(self):

        used_memory = self.total_memory - self.available_memory
        usage_percentage = (used_memory / self.total_memory * 100) if self.total_memory > 0 else 0

        return {
            'Total': f"{self.total_memory} MB",
            'Usada': f"{used_memory} MB",
            'Disponible': f"{self.available_memory} MB",
            'Uso': f"{usage_percentage:.1f}%"
        }

    def get_cpu_usage(self):

        usage_percentage = (self.cpu_in_use / self.num_cpus * 100) if self.num_cpus > 0 else 0

        return {
            'Total': self.num_cpus,
            'En Uso': self.cpu_in_use,
            'Disponible': self.num_cpus - self.cpu_in_use,
            'Uso': f"{usage_percentage:.1f}%"
        }

    def get_statistics(self):

        mem_usage = self.get_memory_usage()
        cpu_usage = self.get_cpu_usage()

        return {
            'CPU Total': cpu_usage['Total'],
            'CPU en Uso': cpu_usage['En Uso'],
            'Memoria Total': mem_usage['Total'],
            'Memoria Usada': mem_usage['Usada'],
            'Memoria Disponible': mem_usage['Disponible'],
            'Uso Memoria': mem_usage['Uso'],
            'Procesos con Memoria': len(self.memory_allocations)
        }

    def _log_event(self, message, event_type="INFO"):

        event = {
            'type': event_type,
            'message': message
        }
        self.event_log.append(event)

    def get_event_log(self, last_n=10):

        return self.event_log[-last_n:] if last_n > 0 else self.event_log

    def clear_log(self):

        self.event_log = []

    def __str__(self):
        return f"ResourceManager(CPUs={self.num_cpus}, Memoria={self.total_memory}MB)"