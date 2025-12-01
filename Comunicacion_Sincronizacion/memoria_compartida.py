
import time

class SharedMemory:

    def __init__(self, name, size=5):
        self.name = name
        self.size = size
        self.buffer = []
        
        # Estadísticas
        self.total_writes = 0
        self.total_reads = 0
        self.access_log = []
    
    def write(self, process, item):

        if len(self.buffer) >= self.size:
            return False  # Buffer lleno
        
        self.buffer.append(item)
        self.total_writes += 1
        
        # Registrar acceso
        self.access_log.append({
            'action': 'WRITE',
            'process_pid': process.pid,
            'process_name': process.name,
            'item': item,
            'timestamp': time.time(),
            'buffer_size': len(self.buffer)
        })
        
        return True
    
    def read(self, process):

        if not self.buffer:
            return None  # Buffer vacío
        
        item = self.buffer.pop(0)
        self.total_reads += 1
        
        # Registrar acceso
        self.access_log.append({
            'action': 'READ',
            'process_pid': process.pid,
            'process_name': process.name,
            'item': item,
            'timestamp': time.time(),
            'buffer_size': len(self.buffer)
        })
        
        return item
    
    def is_full(self):

        return len(self.buffer) >= self.size
    
    def is_empty(self):

        return len(self.buffer) == 0
    
    def get_items_count(self):

        return len(self.buffer)
    
    def get_buffer_items(self):

        return list(self.buffer)
    
    def get_recent_accesses(self, n=10):

        return self.access_log[-n:] if n > 0 else self.access_log
    
    def get_statistics(self):

        return {
            'Nombre': self.name,
            'Tamaño Total': self.size,
            'Items Actuales': len(self.buffer),
            'Total Escrituras': self.total_writes,
            'Total Lecturas': self.total_reads,
            'Estado': 'LLENO' if self.is_full() else ('VACÍO' if self.is_empty() else 'PARCIAL')
        }
    
    def clear(self):

        self.buffer = []
    
    def __str__(self):
        return f"SharedMemory('{self.name}', {len(self.buffer)}/{self.size} items)"
