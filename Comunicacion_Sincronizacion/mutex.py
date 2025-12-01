class Mutex:

    def __init__(self, name):
        #Inicializa el mutex
        self.name = name
        self.locked = False
        self.owner = None  # Proceso que actualmente tiene el lock
        self.waiting_queue = []  # Procesos esperando adquirir el mutex
        
        # Estadísticas
        self.total_acquires = 0
        self.total_releases = 0
        self.total_blocks = 0
    
    def acquire(self, process, scheduler):

        if not self.locked:
            # Mutex disponible, adquirir
            self.locked = True
            self.owner = process
            self.total_acquires += 1
            return True
        else:
            # Mutex ocupado por otro proceso
            if process not in self.waiting_queue:
                # Bloquear proceso
                scheduler.block_process(
                    process.pid,
                    f"Esperando mutex '{self.name}'"
                )
                self.waiting_queue.append(process)
                self.total_blocks += 1
            return False
    
    def release(self, process, scheduler):

        # Solo el dueño puede liberar
        if self.owner != process:
            return False
        
        self.locked = False
        self.owner = None
        self.total_releases += 1
        
        # Despertar siguiente proceso en cola
        if self.waiting_queue:
            next_process = self.waiting_queue.pop(0)
            scheduler.unblock_process(next_process.pid)
            
            # El proceso despertado adquiere automáticamente
            self.locked = True
            self.owner = next_process
            self.total_acquires += 1
        
        return True
    
    def try_acquire(self, process):

        if not self.locked:
            self.locked = True
            self.owner = process
            self.total_acquires += 1
            return True
        return False
    
    def is_locked(self):

        return self.locked
    
    def get_owner(self):

        return self.owner
    
    def get_waiting_count(self):

        return len(self.waiting_queue)
    
    def get_waiting_processes(self):

        return list(self.waiting_queue)
    
    def get_statistics(self):

        return {
            'Nombre': self.name,
            'Estado': 'BLOQUEADO' if self.locked else 'LIBRE',
            'Owner': f"P{self.owner.pid} ({self.owner.name})" if self.owner else "Ninguno",
            'En Espera': len(self.waiting_queue),
            'Total Adquisiciones': self.total_acquires,
            'Total Liberaciones': self.total_releases,
            'Total Bloqueos': self.total_blocks
        }
    
    def __str__(self):
        status = "LOCKED" if self.locked else "FREE"
        owner_str = f" by P{self.owner.pid}" if self.owner else ""
        return f"Mutex('{self.name}', {status}{owner_str})"
