import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from generators.Congruences import LinealCongruence

import math

class ExponentialDistribution:
    def __init__(self, rate,seed,n):
        self.rate = rate
        self.n = n
        self.seed = seed
        # generador de Ri congruencial lineal con parametros para generar minimo 1 millon de numeros
        self.lcg = LinealCongruence(xo_seed=self.seed,k=551757622, c=12345, g=31)  # Ejemplo de inicialización


    #Genera los numeros Ni bajo una distribucion exponencial
    def generate_exponential(self):
        sequence = self.lcg.generate_sequence(self.n)
        #secuencia de numeros exponenciales con la formula de transformacion inversa
        exponential_sequence = [- (1 / self.rate) * math.log(1 - u) for u in sequence]
        return  sequence,exponential_sequence