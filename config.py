import configparser
import os

class Config:


    def __init__(self, config_file='config.ini'):

        self.config = configparser.ConfigParser()
        
        # Si no existe el archivo, crear uno por defecto
        if not os.path.exists(config_file):
            self._create_default_config(config_file)
        
        # Leer el archivo con codificación UTF-8
        self.config.read(config_file, encoding='utf-8')
        
        # Leer parámetros de recursos
        self.num_cpus = int(self.config.get('Resources', 'num_cpus', fallback=1))
        self.total_memory = int(self.config.get('Resources', 'total_memory', fallback=4096))
        
        # Leer parámetros de planificación
        self.scheduling_algorithm = self.config.get('Scheduling', 'algorithm', fallback='SJF')
        self.time_quantum = int(self.config.get('Scheduling', 'time_quantum', fallback=100))
        
        # Leer parámetros de procesos
        self.min_burst_time = int(self.config.get('Processes', 'min_burst_time', fallback=50))
        self.max_burst_time = int(self.config.get('Processes', 'max_burst_time', fallback=500))
        self.min_memory = int(self.config.get('Processes', 'min_memory', fallback=50))
        self.max_memory = int(self.config.get('Processes', 'max_memory', fallback=300))
        
        # Validar configuración
        self._validate_config()
    
    def _create_default_config(self, config_file):

        default_config = configparser.ConfigParser()
        
        default_config['Resources'] = {
            'num_cpus': '1',
            'total_memory': '4096'
        }

        default_config['Scheduling'] = {
            'algorithm': 'SJF',
            'time_quantum': '100'
        }
        
        default_config['Processes'] = {
            'min_burst_time': '50',
            'max_burst_time': '500',
            'min_memory': '50',
            'max_memory': '300'
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            default_config.write(f)
    
    def _validate_config(self):

        if self.num_cpus <= 0:
            raise ValueError("El número de CPUs debe ser positivo")
        
        if self.total_memory <= 0:
            raise ValueError("La memoria total debe ser positiva")
        
        if self.time_quantum <= 0:
            raise ValueError("El quantum debe ser positivo")

        valid_algorithms = ['SJF', 'Prioridad']
        if self.scheduling_algorithm not in valid_algorithms:
            raise ValueError(f"Algoritmo debe ser uno de: {valid_algorithms}")
    
    def get_summary(self):

        return {
            'CPUs': self.num_cpus,
            'Memoria Total': f"{self.total_memory} MB",
            'Algoritmo de Planificación': self.scheduling_algorithm,
            'Quantum': f"{self.time_quantum} ms",
            'Burst Time': f"{self.min_burst_time}-{self.max_burst_time} ms",
            'Memoria por Proceso': f"{self.min_memory}-{self.max_memory} MB"
        }
