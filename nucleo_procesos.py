from __future__ import annotations
import threading
import time
import random


class Process:
    _id_counter = 0

    READY = "Listo"
    RUNNING = "Ejecutando"
    WAITING = "Esperando"
    TERMINATED = "Terminado"

    def __init__(self, name, burst_time, priority=None, memory_required=100):
        Process._id_counter += 1
        self.pid = Process._id_counter
        self.name = name
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.priority = priority if priority else random.randint(1, 10)
        self.memory_required = memory_required

        self.state = Process.READY
        self.assigned_cpu = False
        self.assigned_memory = 0

        self.arrival_time = 0
        self.start_time = None
        self.finish_time = None
        self.waiting_time = 0
        self.turnaround_time = 0
        self.response_time = None

        self.time_quantum_used = 0

    def set_state(self, new_state):
        old_state = self.state
        self.state = new_state
        return old_state

    def assign_cpu(self):
        self.assigned_cpu = True
        self.set_state(Process.RUNNING)
        if self.start_time is None:
            self.start_time = 0

    def release_cpu(self):
        self.assigned_cpu = False
        if self.remaining_time > 0:
            self.set_state(Process.READY)
        else:
            self.set_state(Process.TERMINATED)

    def execute(self, time_slice):
        if self.state != Process.RUNNING:
            return False

        execution_time = min(time_slice, self.remaining_time)
        self.remaining_time -= execution_time
        self.time_quantum_used += execution_time

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
            self.waiting_time = self.turnaround_time - self.burst_time
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

    @staticmethod
    def reset_counter():
        Process._id_counter = 0

class Scheduler:
    SJF = "SJF"
    PRIORITY = "Prioridad"

    def __init__(self, algorithm=SJF):
        self.algorithm = algorithm
        self.current_time = 0

        self.ready_queue = []
        self.running_process = None
        self.waiting_queue = []
        self.terminated_processes = []

        self.total_processes = 0
        self.context_switches = 0

        self.event_log = []

    def add_process(self, process):
        process.arrival_time = self.current_time
        process.set_state(Process.READY)
        self.ready_queue.append(process)
        self.total_processes += 1

        self._log_event(f"Proceso {process} agregado a cola de listos", "INFO")
        self._sort_ready_queue()

    def _sort_ready_queue(self):
        if self.algorithm == Scheduler.SJF:
            self.ready_queue.sort(key=lambda p: p.remaining_time)
        elif self.algorithm == Scheduler.PRIORITY:
            self.ready_queue.sort(key=lambda p: p.priority)

    def schedule(self):
        if self.running_process:
            return self.running_process

        if not self.ready_queue:
            return None

        next_process = self.ready_queue.pop(0)
        next_process.assign_cpu()
        next_process.reset_quantum()

        if next_process.start_time is None:
            next_process.start_time = self.current_time
            next_process.response_time = self.current_time - next_process.arrival_time

        self.running_process = next_process
        self.context_switches += 1

        self._log_event(f"Proceso {next_process} asignado a CPU ({self.algorithm})", "INFO")
        return next_process

    def execute_current_process(self, time_slice=10):
        if not self.running_process:
            return False

        process = self.running_process
        finished = process.execute(time_slice)
        self.current_time += time_slice

        if finished:
            process.calculate_statistics(self.current_time)
            self.terminated_processes.append(process)
            self.running_process = None
            self._log_event(f"Proceso {process} TERMINADO", "INFO")
            return True

        return False

    def block_process(self, pid, reason="Esperando recurso"):
        if self.running_process and self.running_process.pid == pid:
            process = self.running_process
            process.release_cpu()
            process.set_state(Process.WAITING)
            self.waiting_queue.append(process)
            self.running_process = None
            self._log_event(f"Proceso {process} BLOQUEADO ({reason})", "WARNING")
            return

        for i, process in enumerate(self.ready_queue):
            if process.pid == pid:
                process.set_state(Process.WAITING)
                self.waiting_queue.append(process)
                self.ready_queue.pop(i)
                self._log_event(f"Proceso {process} BLOQUEADO ({reason})", "WARNING")
                return

    def unblock_process(self, pid):
        for i, process in enumerate(self.waiting_queue):
            if process.pid == pid:
                process.set_state(Process.READY)
                self.ready_queue.append(process)
                self.waiting_queue.pop(i)
                self._sort_ready_queue()
                self._log_event(f"Proceso {process} DESBLOQUEADO", "INFO")
                return

    def terminate_process(self, pid):
        # running
        if self.running_process and self.running_process.pid == pid:
            process = self.running_process
            process.set_state(Process.TERMINATED)
            process.calculate_statistics(self.current_time)
            self.terminated_processes.append(process)
            self.running_process = None
            self._log_event(f"Proceso {process} terminado forzadamente", "FORCED")
            return

        # ready
        for i, process in enumerate(self.ready_queue):
            if process.pid == pid:
                process.set_state(Process.TERMINATED)
                process.calculate_statistics(self.current_time)
                self.terminated_processes.append(process)
                self.ready_queue.pop(i)
                self._log_event(f"Proceso {process} terminado forzadamente", "FORCED")
                return

        # waiting
        for i, process in enumerate(self.waiting_queue):
            if process.pid == pid:
                process.set_state(Process.TERMINATED)
                process.calculate_statistics(self.current_time)
                self.terminated_processes.append(process)
                self.waiting_queue.pop(i)
                self._log_event(f"Proceso {process} terminado forzadamente", "FORCED")
                return

    def get_statistics(self):
        if not self.terminated_processes:
            avg_waiting = 0
            avg_turnaround = 0
            avg_response = 0
        else:
            avg_waiting = sum(p.waiting_time for p in self.terminated_processes) / len(self.terminated_processes)
            avg_turnaround = sum(p.turnaround_time for p in self.terminated_processes) / len(self.terminated_processes)
            responses = [p.response_time for p in self.terminated_processes if p.response_time is not None]
            avg_response = sum(responses) / len(responses) if responses else 0

        return {
            'Algoritmo': self.algorithm,
            'Quantum': "N/A",
            'Tiempo Actual': f"{self.current_time} ms",
            'Procesos Totales': self.total_processes,
            'En Ejecución': 1 if self.running_process else 0,
            'En Cola Listos': len(self.ready_queue),
            'Esperando': len(self.waiting_queue),
            'Terminados': len(self.terminated_processes),
            'Context Switches': self.context_switches,
            'Tiempo Espera Promedio': f"{avg_waiting:.2f} ms",
            'Turnaround Promedio': f"{avg_turnaround:.2f} ms",
            'Tiempo Respuesta Promedio': f"{avg_response:.2f} ms"
        }

    def get_all_processes(self):
        return (
            ([self.running_process] if self.running_process else []) +
            self.ready_queue +
            self.waiting_queue +
            self.terminated_processes
        )

    def _log_event(self, message, event_type="INFO"):
        timestamp = f"{self.current_time}ms"
        self.event_log.append({
            'timestamp': timestamp,
            'type': event_type,
            'message': message
        })

    def get_event_log(self, last_n=10):
        return self.event_log[-last_n:] if last_n > 0 else self.event_log

    def clear_log(self):
        self.event_log = []

class SimulationController:
    def __init__(self, scheduler, resource_manager, config, callback=None):
        self.scheduler = scheduler
        self.resource_manager = resource_manager
        self.config = config
        self.callback = callback

        # Usamos el ProcessGenerator definido abajo en este mismo archivo
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
        self.speed = 1.0

        # Probabilidades
        self.prob_create_process = 0.70
        self.prob_block_process = 0.15
        self.prob_unblock_process = 0.05

        self.time_slice = 10
        self.update_interval = 0.1

        # Productor–Consumidor
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

                time.sleep(self.update_interval / self.speed)
            else:
                time.sleep(0.1)

    def _execute_step(self):
        process = self.scheduler.schedule()
        if process:
            finished = self.scheduler.execute_current_process(self.time_slice)
            if finished:
                self.resource_manager.release_resources(process)

    def _execute_random_action(self):
        rand = random.random()
        if rand < self.prob_create_process:
            self._create_random_process()
        elif rand < self.prob_create_process + self.prob_block_process:
            self._block_random_process()
        elif rand < self.prob_create_process + self.prob_block_process + self.prob_unblock_process:
            self._unblock_random_process()

    def _create_random_process(self):
        name = self.generator.generate_process_name()
        burst = self.generator.generate_burst_time()
        priority = self.generator.generate_priority()
        memory = self.generator.generate_memory_required()

        # Process viene de arriba en este archivo
        process = Process(name, burst, priority, memory)

        if not self.resource_manager.has_available_resources(process):
            self.generator.release_name(name)
            return

        success, _ = self.resource_manager.request_resources(process)
        if success:
            self.scheduler.add_process(process)
        else:
            self.generator.release_name(name)

    def _block_random_process(self):
        if self.scheduler.ready_queue:
            process = random.choice(self.scheduler.ready_queue)
            self.scheduler.block_process(process.pid, "Esperando I/O")

    def _unblock_random_process(self):
        if self.scheduler.waiting_queue:
            process = random.choice(self.scheduler.waiting_queue)
            self.scheduler.unblock_process(process.pid)

    def _cleanup_terminated_processes(self):
        for process in self.scheduler.terminated_processes[:]:
            self.generator.release_name(process.name)

    def start_producer_consumer(self, buffer_size=5):
        if self.producer_consumer and self.pc_enabled:
            return (False, "Productor-Consumidor ya está ejecutándose")

        # Importar aquí para evitar importación circular
        from Proyecto_Final_SO.Comunicacion_Sincronizacion.productor_consumidor import ProducerConsumer
        self.producer_consumer = ProducerConsumer(buffer_size)
        self.producer_consumer.create_processes(self.scheduler, self.resource_manager)

        self.pc_enabled = True
        return (True, "Productor-Consumidor iniciado")

    def stop_producer_consumer(self):
        if not self.producer_consumer or not self.pc_enabled:
            return (False, "Productor-Consumidor no está ejecutándose")

        self.producer_consumer.stop(self.scheduler, self.resource_manager)
        self.pc_enabled = False
        return (True, "Productor-Consumidor detenido")

    def get_producer_consumer(self):
        return self.producer_consumer if self.pc_enabled else None

class ProcessGenerator:
    def __init__(self, min_burst_time=50, max_burst_time=500,
                 min_memory=50, max_memory=300,
                 min_interval=1.0, max_interval=3.0):

        self.min_burst_time = min_burst_time
        self.max_burst_time = max_burst_time
        self.min_memory = min_memory
        self.max_memory = max_memory
        self.min_interval = min_interval
        self.max_interval = max_interval

        self.available_names = [
            "Chrome", "Firefox", "Edge", "Safari", "Opera",
            "VSCode", "PyCharm", "Eclipse", "IntelliJ", "Sublime",
            "Discord", "Slack", "Teams", "Zoom", "Skype",
            "Spotify", "VLC", "iTunes", "Photoshop", "Premiere",
            "Word", "Excel", "PowerPoint", "Outlook", "OneNote",
            "Docker", "Git", "Node", "Python", "Java",
            "MySQL", "PostgreSQL", "MongoDB", "Redis", "SQLite",
            "FileExplorer", "Terminal", "Calculator", "Notepad", "Paint",
            "Steam", "Epic", "Minecraft", "League", "Valorant",
            "Antivirus", "Backup", "Update", "Monitor", "TaskManager"
        ]

        self.used_names = set()

    def generate_process_name(self):
        available = [n for n in self.available_names if n not in self.used_names]
        if not available:
            return f"Process{random.randint(1000, 9999)}"
        name = random.choice(available)
        self.used_names.add(name)
        return name

    def generate_burst_time(self):
        if random.random() < 0.7:
            return random.randint(self.min_burst_time,
                                  (self.min_burst_time + self.max_burst_time)//2)
        else:
            return random.randint((self.min_burst_time + self.max_burst_time)//2,
                                  self.max_burst_time)

    def generate_priority(self):
        p = int(random.gauss(5, 2))
        return max(1, min(10, p))

    def generate_memory_required(self):
        if random.random() < 0.7:
            return random.randint(self.min_memory,
                                  (self.min_memory + self.max_memory)//2)
        else:
            return random.randint((self.min_memory + self.max_memory)//2,
                                  self.max_memory)

    def get_next_interval(self):
        return random.uniform(self.min_interval, self.max_interval)

    def release_name(self, name):
        self.used_names.discard(name)

    def reset(self):
        self.used_names.clear()