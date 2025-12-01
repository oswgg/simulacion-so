try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext, messagebox
except ImportError:
    print("Error: tkinter no está disponible")
    exit(1)

from Proyecto_Final_SO.config import Config
from planificador import Scheduler
from administrador_recursos import ResourceManager
from simulacion_control import SimulationController
from proceso import Process


class ProcessSchedulerGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Planificación de Procesos")
        self.root.geometry("1400x850")
        self.root.configure(bg='#2C3E50')

        # Cargar configuración
        self.config = Config()

        # Crear componentes
        self.scheduler = Scheduler(
            algorithm=self.config.scheduling_algorithm
        )
        self.resource_manager = ResourceManager(
            num_cpus=self.config.num_cpus,
            total_memory=self.config.total_memory
        )
        self.controller = SimulationController(
            self.scheduler,
            self.resource_manager,
            self.config,
            callback=self.update_display
        )

        # Desactivar creación automática
        self.controller.prob_create_process = 0.0

        # Colores
        self.color_ready = '#4CAF50'  # Verde
        self.color_running = '#2196F3'  # Azul
        self.color_waiting = '#FF9800'  # Naranja
        self.color_terminated = '#9E9E9E'  # Gris

        self._create_widgets()
        self.update_display()
        self.root.after(500, self._periodic_update)

    def _create_widgets(self):

        # Título
        title_frame = tk.Frame(self.root, bg='#34495E', height=50)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)

        tk.Label(
            title_frame,
            text="Simulador de Planificación de Procesos - Memoria Compartida + Mutex",
            font=('Arial', 16, 'bold'),
            bg='#34495E',
            fg='white'
        ).pack(pady=10)

        # Frame principal
        main_frame = tk.Frame(self.root, bg='#2C3E50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Panel superior (Controles + Estadísticas)
        top_panel = tk.Frame(main_frame, bg='#2C3E50')
        top_panel.pack(fill=tk.X, pady=(0, 10))

        self._create_control_panel(top_panel)
        self._create_stats_panel(top_panel)

        # Panel central izquierdo (Colas de procesos)
        center_frame = tk.Frame(main_frame, bg='#2C3E50')
        center_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Cola de procesos
        queue_frame = tk.Frame(center_frame, bg='#ECF0F1', relief=tk.RAISED, bd=2)
        queue_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self._create_queue_panel(queue_frame)

        # Productor-Consumidor
        pc_frame = tk.Frame(center_frame, bg='#ECF0F1', relief=tk.RAISED, bd=2)
        pc_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self._create_producer_consumer_panel(pc_frame)

    def _create_control_panel(self, parent):

        frame = tk.LabelFrame(parent, text="Control de Simulación",
                              font=('Arial', 10, 'bold'),
                              bg='#ECF0F1', fg='#2C3E50', padx=15, pady=10)
        frame.pack(side=tk.LEFT, padx=(0, 10), fill=tk.BOTH)

        # Botones en columnas
        btn_frame = tk.Frame(frame, bg='#ECF0F1')
        btn_frame.pack()

        # Fila 1
        tk.Button(
            btn_frame,
            text="Crear Proceso",
            command=self.create_process_manual,
            bg='#27AE60',
            fg='white',
            font=('Arial', 9, 'bold'),
            width=16,
            height=2,
            cursor='hand2'
        ).grid(row=0, column=0, padx=5, pady=5)

        tk.Button(
            btn_frame,
            text="▶ Iniciar",
            command=self.start_simulation,
            bg='#3498DB',
            fg='white',
            font=('Arial', 9, 'bold'),
            width=16,
            height=2,
            cursor='hand2'
        ).grid(row=0, column=1, padx=5, pady=5)

        # Fila 2
        tk.Button(
            btn_frame,
            text="⏸ Pausar",
            command=self.pause_simulation,
            bg='#F39C12',
            fg='white',
            font=('Arial', 9, 'bold'),
            width=16,
            height=2,
            cursor='hand2'
        ).grid(row=1, column=0, padx=5, pady=5)

        tk.Button(
            btn_frame,
            text="⏹ Detener",
            command=self.stop_simulation,
            bg='#E74C3C',
            fg='white',
            font=('Arial', 9, 'bold'),
            width=16,
            height=2,
            cursor='hand2'
        ).grid(row=1, column=1, padx=5, pady=5)

        # Fila 3: Terminar Proceso
        tk.Button(
            btn_frame,
            text="Terminar Proceso",
            command=self.show_terminate_dialog,
            bg='#C0392B',
            fg='white',
            font=('Arial', 9, 'bold'),
            width=34,
            height=1,
            cursor='hand2'
        ).grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        # Separador
        tk.Frame(frame, bg='#BDC3C7', height=2).pack(fill=tk.X, pady=10)

        # Productor-Consumidor
        tk.Label(frame, text="Demostración P-C:", bg='#ECF0F1',
                 font=('Arial', 9, 'bold')).pack()

        tk.Button(
            frame,
            text="Iniciar Productor-Consumidor",
            command=self.start_pc,
            bg='#8E44AD',
            fg='white',
            font=('Arial', 9, 'bold'),
            width=20,
            height=2,
            cursor='hand2'
        ).pack(pady=5)

        tk.Button(
            frame,
            text="Detener Productor-Consumidor",
            command=self.stop_pc,
            bg='#C0392B',
            fg='white',
            font=('Arial', 9, 'bold'),
            width=20,
            height=2,
            cursor='hand2'
        ).pack(pady=5)

        # Velocidad
        speed_frame = tk.Frame(frame, bg='#ECF0F1')
        speed_frame.pack(pady=(10, 0))

        tk.Label(speed_frame, text="Velocidad:", bg='#ECF0F1',
                 font=('Arial', 9)).pack()

        self.speed_var = tk.DoubleVar(value=1.0)
        speed_scale = tk.Scale(speed_frame, from_=0.5, to=3.0, resolution=0.5,
                               orient=tk.HORIZONTAL, variable=self.speed_var,
                               command=self.change_speed, bg='#ECF0F1',
                               length=180)
        speed_scale.pack()

        self.speed_label = tk.Label(speed_frame, text="1.0x", bg='#ECF0F1',
                                    font=('Arial', 10, 'bold'))
        self.speed_label.pack()

    def _create_stats_panel(self, parent):

        container = tk.Frame(parent, bg='#2C3E50')
        container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        container.columnconfigure(0, weight=3)
        container.columnconfigure(1, weight=2)
        container.rowconfigure(0, weight=1)

        stats_frame = tk.LabelFrame(
            container,
            text="Estadísticas",
            font=('Arial', 10, 'bold'),
            bg='#ECF0F1',
            fg='#2C3E50',
            padx=15,
            pady=10
        )
        stats_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 10))

        self.stats_labels = {}
        stats = [
            ('Algoritmo', ''),
            ('Tiempo', ''),
            ('Procesos Totales', ''),
            ('En Cola Listos', ''),
            ('En Espera', ''),
            ('Terminados', ''),
            ('Tiempo Espera Prom.', ''),
            ('CPU Uso', ''),
            ('Memoria Uso', '')
        ]

        row = 0
        col = 0
        for label_text, value in stats:
            stat_row = tk.Frame(stats_frame, bg='#ECF0F1')
            stat_row.grid(row=row, column=col, sticky='w', padx=10, pady=3)

            tk.Label(stat_row, text=label_text + ":", bg='#ECF0F1',
                     font=('Arial', 9), width=18, anchor='w').pack(side=tk.LEFT)

            value_label = tk.Label(
                stat_row, text=value, bg='#ECF0F1',
                font=('Arial', 9, 'bold'), fg='#2C3E50',
                width=15, anchor='w'
            )
            value_label.pack(side=tk.LEFT)

            self.stats_labels[label_text] = value_label

            col += 1
            if col > 2:
                col = 0
                row += 1

        log_frame = tk.LabelFrame(
            container,
            text="Log de Eventos",
            font=('Arial', 10, 'bold'),
            bg='#ECF0F1',
            fg='#2C3E50',
            padx=10,
            pady=10
        )
        log_frame.grid(row=0, column=1, sticky='nsew')

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=12,
            font=('Courier', 8),
            bg='#1E1E1E',
            fg='#AABBCC',
            insertbackground='white'
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # COLORES DEL LOG
        self.log_text.tag_config('INFO', foreground='#4CAF50')
        self.log_text.tag_config('WARNING', foreground='#FF9800')
        self.log_text.tag_config('ERROR', foreground='#E53935')
        self.log_text.tag_config('FORCED', foreground='#FF3333')  # 🔥 rojo brillante

    def _create_queue_panel(self, parent):
        # Título
        tk.Label(parent, text="Cola de Procesos", font=('Arial', 12, 'bold'),
                 bg='#ECF0F1', fg='#2C3E50').pack(pady=10)

        # Leyenda de colores
        legend_frame = tk.Frame(parent, bg='#ECF0F1')
        legend_frame.pack()

        self._create_legend_item(legend_frame, "Listo", self.color_ready)
        self._create_legend_item(legend_frame, "Ejecutando", self.color_running)
        self._create_legend_item(legend_frame, "Esperando", self.color_waiting)
        self._create_legend_item(legend_frame, "Terminado", self.color_terminated)

        # Canvas para dibujar procesos
        canvas_frame = tk.Frame(parent, bg='white', relief=tk.SUNKEN, bd=2)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.queue_canvas = tk.Canvas(canvas_frame, bg='white', highlightthickness=0)
        self.queue_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Bind clic derecho para terminar procesos
        self.queue_canvas.bind("<Button-3>", self.on_right_click)

        # Menú contextual
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label=" Terminar Proceso Forzadamente", command=self.terminate_selected_process)
        self.selected_process = None

    def _create_producer_consumer_panel(self, parent):
        # Título
        tk.Label(
            parent,
            text="Productor-Consumidor\n(Memoria Compartida + Mutex)",
            font=('Arial', 11, 'bold'),
            bg='#ECF0F1',
            fg='#8E44AD'
        ).pack(pady=10)

        # Canvas para visualización
        canvas_frame = tk.Frame(parent, bg='white', relief=tk.SUNKEN, bd=2)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.pc_canvas = tk.Canvas(canvas_frame, bg='white', highlightthickness=0)
        self.pc_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _create_legend_item(self, parent, text, color):
        item = tk.Frame(parent, bg='#ECF0F1')
        item.pack(side=tk.LEFT, padx=10)

        color_box = tk.Canvas(item, width=20, height=20, bg=color,
                              highlightthickness=1, highlightbackground='#34495E')
        color_box.pack(side=tk.LEFT, padx=(0, 5))

        tk.Label(item, text=text, bg='#ECF0F1', font=('Arial', 9)).pack(side=tk.LEFT)

    def draw_all_processes(self):
        self.queue_canvas.delete('all')

        width = self.queue_canvas.winfo_width()
        height = self.queue_canvas.winfo_height()

        # Recopilar todos los procesos
        all_processes = []

        # Proceso en ejecución
        if self.scheduler.running_process:
            all_processes.append(self.scheduler.running_process)

        # Cola de listos
        all_processes.extend(self.scheduler.ready_queue)

        # Cola de espera
        all_processes.extend(self.scheduler.waiting_queue)

        # Procesos terminados (últimos 5)
        all_processes.extend(self.scheduler.terminated_processes[-5:])

        if not all_processes:
            self.queue_canvas.create_text(
                20, 20,  # posición fija arriba a la izquierda
                text="No hay procesos\n\nPresiona 'Crear Proceso' para agregar",
                font=('Arial', 11),
                fill='#95A5A6',
                justify='left',
                anchor='nw'  # north-west: esquina superior izquierda
            )
            return

        # Calcular layout
        box_width = 110
        box_height = 75
        margin = 12

        # Calcular cuántos caben por fila
        boxes_per_row = max(1, (width - 2 * margin) // (box_width + margin))

        # Dibujar procesos
        x = margin
        y = margin
        col = 0

        for proc in all_processes:
            # Color según estado
            if proc.state == Process.READY:
                color = self.color_ready
                state_text = "LISTO"
            elif proc.state == Process.RUNNING:
                color = self.color_running
                state_text = "EJECUTANDO"
            elif proc.state == Process.WAITING:
                color = self.color_waiting
                state_text = "ESPERANDO"
            else:
                color = self.color_terminated
                state_text = "TERMINADO"

            # Dibujar rectángulo
            self.queue_canvas.create_rectangle(
                x, y, x + box_width, y + box_height,
                fill=color, outline='#34495E', width=2
            )

            # Información del proceso
            text_y = y + 12
            self.queue_canvas.create_text(
                x + box_width // 2, text_y,
                text=f"P{proc.pid}",
                font=('Arial', 11, 'bold'),
                fill='white'
            )

            text_y += 18
            self.queue_canvas.create_text(
                x + box_width // 2, text_y,
                text=proc.name,
                font=('Arial', 8),
                fill='white'
            )

            text_y += 16
            self.queue_canvas.create_text(
                x + box_width // 2, text_y,
                text=state_text,
                font=('Arial', 7, 'bold'),
                fill='white'
            )

            text_y += 14
            self.queue_canvas.create_text(
                x + box_width // 2, text_y,
                text=f"Prior:{proc.priority} | {proc.remaining_time}ms",
                font=('Arial', 7),
                fill='white'
            )

            # Siguiente posición
            col += 1
            if col >= boxes_per_row:
                col = 0
                x = margin
                y += box_height + margin
            else:
                x += box_width + margin

    def draw_producer_consumer(self):
        self.pc_canvas.delete('all')

        pc = self.controller.get_producer_consumer()

        if not pc:
            # No hay demostración activa
            width = self.pc_canvas.winfo_width()
            height = self.pc_canvas.winfo_height()

            self.pc_canvas.create_text(
                20, 20,  # posición fija arriba a la izquierda
                text="Inicia la demostración\nProductor–Consumidor",
                font=('Arial', 11),
                fill='#95A5A6',
                justify='left',
                anchor='nw'  # esquina superior izquierda
            )
            return

        width = self.pc_canvas.winfo_width()
        height = self.pc_canvas.winfo_height()

        # Dibujar buffer compartido
        buffer_y = 50
        self._draw_buffer(pc, buffer_y, width)

        # Dibujar mutex
        mutex_y = buffer_y + 120
        self._draw_mutex(pc, mutex_y, width)

        # Dibujar estadísticas
        stats_y = mutex_y + 100
        self._draw_pc_stats(pc, stats_y, width)

    def _draw_buffer(self, pc, y, width):
        # Título
        self.pc_canvas.create_text(
            width // 2, y,
            text="MEMORIA COMPARTIDA (Buffer)",
            font=('Arial', 10, 'bold'),
            fill='#2C3E50'
        )

        # Buffer
        items = pc.get_buffer_items()
        buffer_size = pc.shared_memory.size

        box_width = 60
        box_height = 50
        spacing = 10
        total_width = buffer_size * (box_width + spacing) - spacing
        start_x = (width - total_width) // 2

        y_pos = y + 30

        for i in range(buffer_size):
            x_pos = start_x + i * (box_width + spacing)

            if i < len(items):
                # Hay item
                color = '#27AE60'
                self.pc_canvas.create_rectangle(
                    x_pos, y_pos, x_pos + box_width, y_pos + box_height,
                    fill=color, outline='#1E8449', width=2
                )
                self.pc_canvas.create_text(
                    x_pos + box_width // 2, y_pos + box_height // 2,
                    text=items[i],
                    font=('Arial', 7, 'bold'),
                    fill='white'
                )
            else:
                # Vacío
                color = '#ECF0F1'
                self.pc_canvas.create_rectangle(
                    x_pos, y_pos, x_pos + box_width, y_pos + box_height,
                    fill=color, outline='#BDC3C7', width=2
                )
                self.pc_canvas.create_text(
                    x_pos + box_width // 2, y_pos + box_height // 2,
                    text="VACÍO",
                    font=('Arial', 7),
                    fill='#95A5A6'
                )

        # Contador
        self.pc_canvas.create_text(
            width // 2, y_pos + box_height + 20,
            text=f"{len(items)}/{buffer_size} items",
            font=('Arial', 9, 'bold'),
            fill='#34495E'
        )

    def _draw_mutex(self, pc, y, width):
        # Título
        self.pc_canvas.create_text(
            width // 2, y,
            text="MUTEX (Exclusión Mutua)",
            font=('Arial', 10, 'bold'),
            fill='#2C3E50'
        )

        mutex = pc.mutex

        y_pos = y + 30

        # Estado del mutex
        if mutex.is_locked():
            color = '#E74C3C'
            status = " BLOQUEADO "
            owner_text = f"Owner: P{mutex.owner.pid} ({mutex.owner.name})"
        else:
            color = '#27AE60'
            status = " LIBRE "
            owner_text = "Owner: Ninguno"

        # Rectángulo del mutex
        box_width = 200
        box_height = 60
        x_pos = (width - box_width) // 2

        self.pc_canvas.create_rectangle(
            x_pos, y_pos, x_pos + box_width, y_pos + box_height,
            fill=color, outline='#2C3E50', width=2
        )

        self.pc_canvas.create_text(
            x_pos + box_width // 2, y_pos + 20,
            text=status,
            font=('Arial', 11, 'bold'),
            fill='white'
        )

        self.pc_canvas.create_text(
            x_pos + box_width // 2, y_pos + 40,
            text=owner_text,
            font=('Arial', 8),
            fill='white'
        )

    def _draw_pc_stats(self, pc, y, width):
        stats = pc.get_statistics()

        # Título
        self.pc_canvas.create_text(
            width // 2, y,
            text="ESTADÍSTICAS",
            font=('Arial', 10, 'bold'),
            fill='#2C3E50'
        )

        y_pos = y + 25

        # Estadísticas en columnas
        stats_text = f"Producidos: {stats['Items Producidos']}    Consumidos: {stats['Items Consumidos']}    En Buffer: {stats['En Buffer']}"

        self.pc_canvas.create_text(
            width // 2, y_pos,
            text=stats_text,
            font=('Arial', 9),
            fill='#34495E'
        )

    def update_display(self):
        # Dibujar procesos
        self.draw_all_processes()

        # Dibujar productor-consumidor
        self.draw_producer_consumer()

        # Actualizar estadísticas
        stats = self.scheduler.get_statistics()
        self.stats_labels['Algoritmo'].config(text=stats['Algoritmo'])
        self.stats_labels['Tiempo'].config(text=stats['Tiempo Actual'])
        self.stats_labels['Procesos Totales'].config(text=stats['Procesos Totales'])
        self.stats_labels['En Cola Listos'].config(text=stats['En Cola Listos'])
        self.stats_labels['En Espera'].config(text=stats['Esperando'])
        self.stats_labels['Terminados'].config(text=stats['Terminados'])
        self.stats_labels['Tiempo Espera Prom.'].config(text=stats['Tiempo Espera Promedio'])

        # Recursos
        cpu_usage = self.resource_manager.get_cpu_usage()
        mem_usage = self.resource_manager.get_memory_usage()
        self.stats_labels['CPU Uso'].config(text=cpu_usage['Uso'])
        self.stats_labels['Memoria Uso'].config(text=mem_usage['Uso'])

        # Actualizar log
        self._update_log()

    def _update_log(self):
        events = self.scheduler.get_event_log(last_n=10)

        self.log_text.delete('1.0', tk.END)

        for event in events:
            timestamp = event['timestamp']
            event_type = event['type']
            message = event['message']

            line = f"[{timestamp}] {message}\n"
            self.log_text.insert(tk.END, line, event_type)

        self.log_text.see(tk.END)

    def _periodic_update(self):
        if self.controller.running and not self.controller.paused:
            self.update_display()

        self.root.after(500, self._periodic_update)

    def create_process_manual(self):
        # Generar parámetros aleatorios
        name = self.controller.generator.generate_process_name()
        burst = self.controller.generator.generate_burst_time()
        priority = self.controller.generator.generate_priority()
        memory = self.controller.generator.generate_memory_required()

        # Crear proceso
        process = Process(name, burst, priority, memory)

        # Verificar recursos
        if not self.resource_manager.has_available_resources(process):
            messagebox.showerror(
                "Error",
                f"Memoria insuficiente para {process}\n"
                f"Requiere: {memory} MB\n"
                f"Disponible: {self.resource_manager.available_memory} MB"
            )
            self.controller.generator.release_name(name)
            return

        # Asignar recursos
        success, msg = self.resource_manager.request_resources(process)

        if success:
            # Agregar al scheduler
            self.scheduler.add_process(process)
            messagebox.showinfo(
                "Proceso Creado",
                f"Proceso creado exitosamente:\n\n"
                f"PID: {process.pid}\n"
                f"Nombre: {process.name}\n"
                f"Burst Time: {process.burst_time} ms\n"
                f"Prioridad: {process.priority}\n"
                f"Memoria: {process.memory_required} MB"
            )
            self.update_display()
        else:
            messagebox.showerror("Error", msg)
            self.controller.generator.release_name(name)

    def start_simulation(self):
        self.controller.start()

    def pause_simulation(self):
        if self.controller.running:
            if self.controller.paused:
                self.controller.resume()
            else:
                self.controller.pause()

    def stop_simulation(self):
        self.controller.stop()
        self.update_display()

    def change_speed(self, value):
        speed = float(value)
        self.controller.set_speed(speed)
        self.speed_label.config(text=f"{speed}x")

    def start_pc(self):
        success, msg = self.controller.start_producer_consumer(buffer_size=5)

        if success:
            messagebox.showinfo("Productor-Consumidor", msg)
            self.update_display()
        else:
            messagebox.showwarning("Productor-Consumidor", msg)

    def stop_pc(self):
        success, msg = self.controller.stop_producer_consumer()

        if success:
            messagebox.showinfo("Productor-Consumidor", msg)
            self.update_display()
        else:
            messagebox.showwarning("Productor-Consumidor", msg)

    def on_right_click(self, event):
        # Obtener coordenadas del clic
        x, y = event.x, event.y

        # Buscar proceso en esa posición
        process = self.get_process_at_position(x, y)

        if process and process.state != Process.TERMINATED:
            self.selected_process = process
            # Mostrar menú contextual
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()

    def get_process_at_position(self, x, y):
        width = self.queue_canvas.winfo_width()

        # Recopilar todos los procesos
        all_processes = []
        if self.scheduler.running_process:
            all_processes.append(self.scheduler.running_process)
        all_processes.extend(self.scheduler.ready_queue)
        all_processes.extend(self.scheduler.waiting_queue)
        all_processes.extend(self.scheduler.terminated_processes[-5:])

        if not all_processes:
            return None

        # Calcular layout (mismo que draw_all_processes)
        box_width = 110
        box_height = 75
        margin = 12
        boxes_per_row = max(1, (width - 2 * margin) // (box_width + margin))

        # Verificar cada proceso
        pos_x = margin
        pos_y = margin
        col = 0

        for proc in all_processes:
            # Verificar si el clic está dentro de este rectángulo
            if (pos_x <= x <= pos_x + box_width and
                    pos_y <= y <= pos_y + box_height):
                return proc

            # Siguiente posición
            col += 1
            if col >= boxes_per_row:
                col = 0
                pos_x = margin
                pos_y += box_height + margin
            else:
                pos_x += box_width + margin

        return None

    def terminate_selected_process(self):
        if not self.selected_process:
            return

        process = self.selected_process

        # Confirmar
        result = messagebox.askyesno(
            "Terminar Proceso Forzadamente",
            f"¿Está seguro de terminar forzadamente el proceso?\n\n"
            f"PID: {process.pid}\n"
            f"Nombre: {process.name}\n"
            f"Estado: {process.state}\n"
            f"Tiempo Restante: {process.remaining_time} ms\n\n"
            f"Esta acción liberará sus recursos abruptamente."
        )

        if result:
            # Liberar recursos primero
            self.resource_manager.release_resources(process)

            # Terminar proceso
            self.scheduler.terminate_process(process.pid)

            messagebox.showinfo(
                "Proceso Terminado",
                f"Proceso P{process.pid} ({process.name}) terminado forzadamente.\n"
                f"Recursos liberados."
            )

            self.update_display()

        self.selected_process = None

    def show_terminate_dialog(self):
        # Recopilar procesos activos (no terminados)
        active_processes = []

        if self.scheduler.running_process:
            active_processes.append(self.scheduler.running_process)
        active_processes.extend(self.scheduler.ready_queue)
        active_processes.extend(self.scheduler.waiting_queue)

        if not active_processes:
            messagebox.showinfo(
                "Terminar Proceso",
                "No hay procesos activos para terminar."
            )
            return

        # Crear ventana de selección
        dialog = tk.Toplevel(self.root)
        dialog.title("Terminar Proceso Forzadamente")
        dialog.geometry("400x300")
        dialog.configure(bg='#ECF0F1')

        tk.Label(
            dialog,
            text="Seleccione el proceso a terminar:",
            font=('Arial', 11, 'bold'),
            bg='#ECF0F1'
        ).pack(pady=10)

        # Lista de procesos
        listbox_frame = tk.Frame(dialog, bg='#ECF0F1')
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(
            listbox_frame,
            font=('Courier', 9),
            yscrollcommand=scrollbar.set,
            height=10
        )
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        # Agregar procesos a la lista
        for proc in active_processes:
            item = f"P{proc.pid:<3} | {proc.name:<15} | {proc.state:<10} | {proc.remaining_time:>5}ms"
            listbox.insert(tk.END, item)

        # Función de terminación
        def terminate():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("Advertencia", "Seleccione un proceso")
                return

            index = selection[0]
            process = active_processes[index]

            # Liberar recursos
            self.resource_manager.release_resources(process)

            # Terminar
            self.scheduler.terminate_process(process.pid)

            messagebox.showinfo(
                "Proceso Terminado",
                f"Proceso P{process.pid} ({process.name}) terminado forzadamente."
            )

            dialog.destroy()
            self.update_display()

        # Botones
        btn_frame = tk.Frame(dialog, bg='#ECF0F1')
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame,
            text=" Terminar Proceso",
            command=terminate,
            bg='#E74C3C',
            fg='white',
            font=('Arial', 10, 'bold'),
            width=20,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="Cancelar",
            command=dialog.destroy,
            bg='#95A5A6',
            fg='white',
            font=('Arial', 10, 'bold'),
            width=20,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)


def main():
    root = tk.Tk()
    app = ProcessSchedulerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
