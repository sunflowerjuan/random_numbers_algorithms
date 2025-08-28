import math

from abc import ABC, abstractmethod


# Clase abstracta para generadores de congruencias
class Congruences(ABC):
    def __init__(self, xo_seed,g):
        self.xo_seed = xo_seed

        self.m = int(math.pow(2, g))
        
    # Genera la siguiente semilla y retorna un número Ri
    @abstractmethod
    def next(self):
        pass
    
    # Genera la secuencia de numeros pseudoaleatorios Ri con un parametro n (Tamaño de la secuencia)
    def generate_sequence(self, n):
        sequence = []
        for _ in range(n):
            sequence.append(self.next())
        return sequence
    
    # Valida si los parametros cumplen con el teorema de Hull-Dobell
    @abstractmethod
    def hull_dobell_validation(self):
        pass
    
    # Calcula el periodo del generador
    def get_period(self):
        if self.hull_dobell_validation():
            return self.m  # Periodo máximo

        seen = {}
        current_seed = self.xo_seed
        period = 0
        # detecta cuando la secuencia comienza a repetirse
        while current_seed not in seen:
            seen[current_seed] = period
            current_seed = (self.a * current_seed + self.c) % self.m
            period += 1
        return period
    
