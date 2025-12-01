"""
Generador de Procesos Aleatorios
Crea procesos con nombres, burst times, prioridades y memoria aleatorios
"""
import random

class ProcessGenerator:

    #Genera procesos aleatorios para el simulador


    def __init__(self, min_burst_time=50, max_burst_time=500,
                 min_memory=50, max_memory=300,
                 min_interval=1.0, max_interval=3.0):

        #Inicializa el generador de procesos

        self.min_burst_time = min_burst_time
        self.max_burst_time = max_burst_time
        self.min_memory = min_memory
        self.max_memory = max_memory
        self.min_interval = min_interval
        self.max_interval = max_interval
        
        # Lista de nombres de procesos comunes
        self.available_names = [
            # Navegadores
            "Chrome", "Firefox", "Edge", "Safari", "Opera",
            # Editores/IDEs
            "VSCode", "PyCharm", "Eclipse", "IntelliJ", "Sublime",
            # Comunicación
            "Discord", "Slack", "Teams", "Zoom", "Skype",
            # Multimedia
            "Spotify", "VLC", "iTunes", "Photoshop", "Premiere",
            # Productividad
            "Word", "Excel", "PowerPoint", "Outlook", "OneNote",
            # Desarrollo
            "Docker", "Git", "Node", "Python", "Java",
            # Bases de datos
            "MySQL", "PostgreSQL", "MongoDB", "Redis", "SQLite",
            # Utilidades
            "FileExplorer", "Terminal", "Calculator", "Notepad", "Paint",
            # Juegos
            "Steam", "Epic", "Minecraft", "League", "Valorant",
            # Sistema
            "Antivirus", "Backup", "Update", "Monitor", "TaskManager"
        ]
        
        self.used_names = set()
    
    def generate_process_name(self):

        # Obtener nombres disponibles
        available = [name for name in self.available_names if name not in self.used_names]
        
        if not available:
            # Si no hay nombres disponibles, generar uno genérico
            return f"Process{random.randint(1000, 9999)}"
        
        # Seleccionar nombre aleatorio
        name = random.choice(available)
        self.used_names.add(name)
        
        return name
    
    def generate_burst_time(self):

        if random.random() < 0.7:
            # 70% procesos cortos (mitad inferior del rango)
            return random.randint(self.min_burst_time, 
                                 (self.min_burst_time + self.max_burst_time) // 2)
        else:
            # 30% procesos largos (mitad superior del rango)
            return random.randint((self.min_burst_time + self.max_burst_time) // 2, 
                                 self.max_burst_time)
    
    def generate_priority(self):

        # Distribución normal centrada en 5
        priority = int(random.gauss(5, 2))
        
        # Limitar entre 1 y 10
        return max(1, min(10, priority))
    
    def generate_memory_required(self):

        if random.random() < 0.7:
            # 70% procesos con poca memoria
            return random.randint(self.min_memory, 
                                 (self.min_memory + self.max_memory) // 2)
        else:
            # 30% procesos con mucha memoria
            return random.randint((self.min_memory + self.max_memory) // 2, 
                                 self.max_memory)
    
    def get_next_interval(self):

        return random.uniform(self.min_interval, self.max_interval)
    
    def release_name(self, name):

        if name in self.used_names:
            self.used_names.remove(name)
    
    def reset(self):

        self.used_names.clear()
    
    def get_stats(self):

        return {
            'Nombres Totales': len(self.available_names),
            'Nombres Usados': len(self.used_names),
            'Nombres Disponibles': len(self.available_names) - len(self.used_names),
            'Rango Burst Time': f"{self.min_burst_time}-{self.max_burst_time} ms",
            'Rango Memoria': f"{self.min_memory}-{self.max_memory} MB",
            'Intervalo': f"{self.min_interval}-{self.max_interval} s"
        }
