from Proyecto_Final_SO.proceso import Process
from Proyecto_Final_SO.Comunicacion_Sincronizacion.memoria_compartida import SharedMemory
from Proyecto_Final_SO.Comunicacion_Sincronizacion.mutex import Mutex
import random

class ProducerConsumer:


    def __init__(self, buffer_size=5):

        # Memoria compartida (buffer)
        self.shared_memory = SharedMemory("ProducerConsumerBuffer", buffer_size)
        
        # Mutex para exclusión mutua
        self.mutex = Mutex("BufferMutex")
        
        # Procesos
        self.producer = None
        self.consumer = None
        
        # Estadísticas
        self.items_produced = 0
        self.items_consumed = 0
        self.item_counter = 0
        
        # Control
        self.running = False
        self.producer_blocked_by_full = False
        self.consumer_blocked_by_empty = False
    
    def create_processes(self, scheduler, resource_manager):

        # Crear Productor
        self.producer = Process(
            "Productor",
            burst_time=999999,  # Proceso de larga duración
            priority=5,
            memory_required=50
        )
        
        # Asignar recursos y agregar al scheduler
        resource_manager.request_resources(self.producer)
        scheduler.add_process(self.producer)
        
        # Crear Consumidor
        self.consumer = Process(
            "Consumidor",
            burst_time=999999,  # Proceso de larga duración
            priority=5,
            memory_required=50
        )
        
        # Asignar recursos y agregar al scheduler
        resource_manager.request_resources(self.consumer)
        scheduler.add_process(self.consumer)
        
        self.running = True
    
    def produce_step(self, scheduler):

        if not self.producer or self.producer.state == Process.TERMINATED:
            return None
        
        # Si el productor está esperando por buffer lleno, intentar despertar
        if self.producer_blocked_by_full:
            if not self.shared_memory.is_full():
                # Hay espacio, despertar
                if self.producer.state == Process.WAITING:
                    scheduler.unblock_process(self.producer.pid)
                self.producer_blocked_by_full = False
            else:
                return "Productor: esperando espacio en buffer"
        
        # Solo producir si el proceso está en ejecución
        if self.producer.state != Process.RUNNING:
            return None
        
        # Paso 1: Intentar adquirir mutex
        if not self.mutex.acquire(self.producer, scheduler):
            return f"Productor: esperando mutex (owner: P{self.mutex.owner.pid})"
        
        # Paso 2: Verificar si hay espacio en buffer
        if self.shared_memory.is_full():
            # Buffer lleno, liberar mutex y bloquear
            self.mutex.release(self.producer, scheduler)
            scheduler.block_process(self.producer.pid, "Buffer lleno")
            self.producer_blocked_by_full = True
            return "Productor: buffer lleno, bloqueado"
        
        # Paso 3: Producir item
        self.item_counter += 1
        item = f"Item #{self.item_counter}"
        self.shared_memory.write(self.producer, item)
        self.items_produced += 1
        
        # Paso 4: Liberar mutex
        self.mutex.release(self.producer, scheduler)
        
        # Paso 5: Si consumidor está esperando buffer vacío, despertarlo
        if self.consumer_blocked_by_empty and not self.shared_memory.is_empty():
            if self.consumer.state == Process.WAITING:
                scheduler.unblock_process(self.consumer.pid)
            self.consumer_blocked_by_empty = False
        
        return f"Productor: producido {item}"
    
    def consume_step(self, scheduler):

        if not self.consumer or self.consumer.state == Process.TERMINATED:
            return None
        
        # Si el consumidor está esperando por buffer vacío, intentar despertar
        if self.consumer_blocked_by_empty:
            if not self.shared_memory.is_empty():
                # Hay items, despertar
                if self.consumer.state == Process.WAITING:
                    scheduler.unblock_process(self.consumer.pid)
                self.consumer_blocked_by_empty = False
            else:
                return "Consumidor: esperando items en buffer"
        
        # Solo consumir si el proceso está en ejecución
        if self.consumer.state != Process.RUNNING:
            return None
        
        # Paso 1: Intentar adquirir mutex
        if not self.mutex.acquire(self.consumer, scheduler):
            return f"Consumidor: esperando mutex (owner: P{self.mutex.owner.pid})"
        
        # Paso 2: Verificar si hay items en buffer
        if self.shared_memory.is_empty():
            # Buffer vacío, liberar mutex y bloquear
            self.mutex.release(self.consumer, scheduler)
            scheduler.block_process(self.consumer.pid, "Buffer vacío")
            self.consumer_blocked_by_empty = True
            return "Consumidor: buffer vacío, bloqueado"
        
        # Paso 3: Consumir item
        item = self.shared_memory.read(self.consumer)
        self.items_consumed += 1
        
        # Paso 4: Liberar mutex
        self.mutex.release(self.consumer, scheduler)
        
        # Paso 5: Si productor está esperando buffer lleno, despertarlo
        if self.producer_blocked_by_full and not self.shared_memory.is_full():
            if self.producer.state == Process.WAITING:
                scheduler.unblock_process(self.producer.pid)
            self.producer_blocked_by_full = False
        
        return f"Consumidor: consumido {item}"
    
    def step(self, scheduler):

        # Decidir aleatoriamente quién va primero (simula concurrencia)
        if random.random() < 0.5:
            msg_p = self.produce_step(scheduler)
            msg_c = self.consume_step(scheduler)
        else:
            msg_c = self.consume_step(scheduler)
            msg_p = self.produce_step(scheduler)
        
        return (msg_p, msg_c)
    
    def stop(self, scheduler, resource_manager):

        # Terminar procesos
        if self.producer:
            resource_manager.release_resources(self.producer)
            scheduler.terminate_process(self.producer.pid)
        
        if self.consumer:
            resource_manager.release_resources(self.consumer)
            scheduler.terminate_process(self.consumer.pid)
        
        self.running = False
    
    def reset(self):

        self.shared_memory.clear()
        self.items_produced = 0
        self.items_consumed = 0
        self.item_counter = 0
        self.producer_blocked_by_full = False
        self.consumer_blocked_by_empty = False
    
    def get_statistics(self):

        stats = {
            'Items Producidos': self.items_produced,
            'Items Consumidos': self.items_consumed,
            'En Buffer': self.shared_memory.get_items_count(),
            'Buffer Size': self.shared_memory.size,
            'Mutex Estado': 'BLOQUEADO' if self.mutex.is_locked() else 'LIBRE',
            'Mutex Owner': f"P{self.mutex.owner.pid} ({self.mutex.owner.name})" if self.mutex.owner else "Ninguno",
            'Productor Estado': self.producer.state if self.producer else "N/A",
            'Consumidor Estado': self.consumer.state if self.consumer else "N/A"
        }
        return stats
    
    def get_buffer_items(self):

        return self.shared_memory.get_buffer_items()
    
    def get_recent_accesses(self, n=10):

        return self.shared_memory.get_recent_accesses(n)
