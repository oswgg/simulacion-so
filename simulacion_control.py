import threading
import time
import random
from Proyecto_Final_SO.generador_proceso import ProcessGenerator
from Proyecto_Final_SO.proceso import Process
from Proyecto_Final_SO.Comunicacion_Sincronizacion.productor_consumidor import ProducerConsumer


class SimulationController:

    def __init__(self, scheduler, resource_manager, config, callback=None):
        self.scheduler = scheduler
        self.resource_manager = resource_manager
        self.config = config
        self.callback = callback

        self.generator = ProcessGenerator(
            min_burst_time=config.min_burst_time,
            max_burst_time=config.max_burst_time,
            min_memory=config.min_memory,
            max_memory=config.max_memory,
            min_interval=1.5,
            max_interval=4.0
        )

        self.running = False
        self.paused = False
        self.thread = None
        self.speed = 1.0  # Velocidad de simulación

        # Probabilidades de acciones
        self.prob_create_process = 0.70
        self.prob_block_process = 0.15
        self.prob_unblock_process = 0.05

        # Intervalo de actualización
        self.time_slice = 10
        self.update_interval = 0.1

        # Productor-Consumidor
        self.producer_consumer = None
        self.pc_enabled = False

    def start(self):

        if not self.running:
            self.running = True
            self.paused = False
            self.thread = threading.Thread(target=self._simulation_loop, daemon=True)
            self.thread.start()

    def pause(self):

        self.paused = True

    def resume(self):

        self.paused = False

    def stop(self):

        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        self.generator.reset()

    def set_speed(self, speed):

        self.speed = max(0.1, min(5.0, speed))

    def _simulation_loop(self):

        while self.running:
            if not self.paused:
                self._execute_step()

                if self.pc_enabled and self.producer_consumer:
                    self.producer_consumer.step(self.scheduler)

                self._execute_random_action()

                self._cleanup_terminated_processes()

                if self.callback:
                    self.callback()

                interval = self.update_interval / self.speed
                time.sleep(interval)
            else:
                time.sleep(0.1)

    def _execute_step(self):

        process = self.scheduler.schedule()

        if process:
            # Ejecutar el proceso por un time slice
            finished = self.scheduler.execute_current_process(self.time_slice)

            if finished:
                # Proceso terminó, liberar recursos
                self.resource_manager.release_resources(process)

    def _execute_random_action(self):

        rand = random.random()

        limite_crear = self.prob_create_process
        limite_bloq = limite_crear + self.prob_block_process
        limite_desbloq = limite_bloq + self.prob_unblock_process

        if rand < limite_crear:
            # Crear nuevo proceso
            self._create_random_process()

        elif rand < limite_bloq:
            # Bloquear un proceso aleatorio
            self._block_random_process()

        elif rand < limite_desbloq:
            # Desbloquear un proceso aleatorio
            self._unblock_random_process()
        else:
            pass

    def _create_random_process(self):

        name = self.generator.generate_process_name()
        burst_time = self.generator.generate_burst_time()
        priority = self.generator.generate_priority()
        memory = self.generator.generate_memory_required()

        # Crear proceso
        process = Process(name, burst_time, priority, memory)

        if not self.resource_manager.has_available_resources(process):
            self.generator.release_name(name)
            return

        # Asignar recursos
        success, msg = self.resource_manager.request_resources(process)

        if success:
            # Agregar al scheduler
            self.scheduler.add_process(process)
        else:
            # No se pudieron asignar recursos
            self.generator.release_name(name)

    def _block_random_process(self):

        if not self.scheduler.ready_queue:
            return

        # Seleccionar proceso aleatorio de la cola de listos
        process = random.choice(self.scheduler.ready_queue)

        # Bloquear el proceso
        self.scheduler.block_process(process.pid, "Esperando I/O")

    def _unblock_random_process(self):

        if not self.scheduler.waiting_queue:
            return

        # Seleccionar proceso aleatorio de la cola de espera
        process = random.choice(self.scheduler.waiting_queue)

        # Desbloquear el proceso
        self.scheduler.unblock_process(process.pid)

    def _cleanup_terminated_processes(self):

        for process in self.scheduler.terminated_processes[:]:
            # Liberar el nombre para reutilización
            self.generator.release_name(process.name)

    def create_process_manual(self, name, burst_time, priority, memory):
        process = Process(name, burst_time, priority, memory)

        # Verificar recursos
        if not self.resource_manager.has_available_resources(process):
            return (False, "Memoria insuficiente")

        # Asignar recursos
        success, msg = self.resource_manager.request_resources(process)

        if success:
            # Agregar al scheduler
            self.scheduler.add_process(process)
            return (True, f"Proceso {process} creado exitosamente")
        else:
            return (False, msg)

    def terminate_process_manual(self, pid):

        all_processes = self.scheduler.get_all_processes()
        process = None

        for p in all_processes:
            if p.pid == pid:
                process = p
                break

        if not process:
            return (False, f"Proceso con PID {pid} no encontrado")

        # Liberar recursos
        self.resource_manager.release_resources(process)

        # Terminar en scheduler
        self.scheduler.terminate_process(pid)

        # Liberar nombre
        self.generator.release_name(process.name)

        return (True, f"Proceso {process} terminado")

    def suspend_process(self, pid):

        self.scheduler.block_process(pid, "Suspendido por usuario")
        return (True, f"Proceso {pid} suspendido")

    def resume_process(self, pid):

        self.scheduler.unblock_process(pid)
        return (True, f"Proceso {pid} reanudado")

    def get_status(self):

        return {
            'running': self.running,
            'paused': self.paused,
            'speed': self.speed,
            'total_processes': self.scheduler.total_processes,
            'ready': len(self.scheduler.ready_queue),
            'running_count': 1 if self.scheduler.running_process else 0,
            'waiting': len(self.scheduler.waiting_queue),
            'terminated': len(self.scheduler.terminated_processes)
        }

    def start_producer_consumer(self, buffer_size=5):

        if self.producer_consumer and self.pc_enabled:
            return (False, "Productor-Consumidor ya está ejecutándose")

        # Crear instancia
        self.producer_consumer = ProducerConsumer(buffer_size)

        # Crear procesos
        self.producer_consumer.create_processes(self.scheduler, self.resource_manager)

        self.pc_enabled = True

        return (True, "Productor-Consumidor iniciado")

    def stop_producer_consumer(self):

        if not self.producer_consumer or not self.pc_enabled:
            return (False, "Productor-Consumidor no está ejecutándose")

        # Detener
        self.producer_consumer.stop(self.scheduler, self.resource_manager)
        self.pc_enabled = False

        return (True, "Productor-Consumidor detenido")

    def get_producer_consumer(self):

        return self.producer_consumer if self.pc_enabled else None
