from Proyecto_Final_SO.proceso import Process


class Scheduler:

    SJF = "SJF"
    PRIORITY = "Prioridad"

    def __init__(self, algorithm=SJF):
        self.algorithm = algorithm
        self.current_time = 0

        # Colas de procesos
        self.ready_queue = []
        self.running_process = None
        self.waiting_queue = []
        self.terminated_processes = []

        # Estadísticas
        self.total_processes = 0
        self.context_switches = 0

        # Log
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
            # SJF: menor tiempo restante primero
            self.ready_queue.sort(key=lambda p: p.remaining_time)
        elif self.algorithm == Scheduler.PRIORITY:
            # Prioridad: menor número = mayor prioridad
            self.ready_queue.sort(key=lambda p: p.priority)

    def schedule(self):
        # Si ya hay proceso ejecutando, seguir con ese
        if self.running_process:
            return self.running_process

        if not self.ready_queue:
            return None

        next_process = self.ready_queue.pop(0)

        next_process.assign_cpu()
        next_process.reset_quantum()  # por compatibilidad con Process

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

    def run_simulation(self, time_limit=1000):
        self.current_time = 0

        while (self.ready_queue or self.running_process) and self.current_time < time_limit:
            process = self.schedule()

            if process:
                self.execute_current_process(time_slice=10)
            else:
                self.current_time += 10

        return self.get_statistics()

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
            'Quantum': "N/A",  # ya no usamos RR
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
        all_processes = []

        if self.running_process:
            all_processes.append(self.running_process)

        all_processes.extend(self.ready_queue)
        all_processes.extend(self.waiting_queue)
        all_processes.extend(self.terminated_processes)

        return all_processes

    def _log_event(self, message, event_type="INFO"):
        timestamp = f"{self.current_time}ms"
        event = {
            'timestamp': timestamp,
            'type': event_type,
            'message': message
        }
        self.event_log.append(event)

    def get_event_log(self, last_n=10):
        return self.event_log[-last_n:] if last_n > 0 else self.event_log

    def clear_log(self):
        self.event_log = []

    def __str__(self):
        return f"Scheduler({self.algorithm})"