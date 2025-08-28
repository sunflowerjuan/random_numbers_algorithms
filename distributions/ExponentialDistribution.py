import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from generators.congruences.Congruences import LinealCongruence

import math

class ExponentialDistribution:
    def __init__(self, rate,seed,n):
        self.rate = rate
        self.n = n
        self.seed = seed
        self.lcg = LinealCongruence(xo_seed=self.seed,k=551757622, c=12345, g=31)  # Ejemplo de inicialización


    def generate_exponential(self):
        sequence = self.lcg.generate_sequence(self.n)
        exponential_sequence = [- (1 / self.rate) * math.log(1 - u) for u in sequence]
        return exponential_sequence