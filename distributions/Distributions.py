
from generators.Congruences import LinealCongruence
import math

class UniformDistribution:
    def __init__(self, seed, n,a,b):
        self.n = n
        self.seed = seed
        self.a = a
        self.b = b
        # generador de Ri congruencial lineal con parametros para generar minimo 1 millon de numeros
        self.lcg = LinealCongruence(xo_seed=self.seed, k=551757622, c=12345, g=31)
        self.ri_secuence = []

    # Genera los numeros Ni bajo una distribucion uniforme
    def generate_uniform(self):
        self.ri_secuence = self.lcg.generate_sequence(self.n)
        # secuencia de numeros uniformes con la formula de transformacion a Ni
        uniform_sequence = [self.a + (self.b - self.a) * r for r in self.ri_secuence]
        return uniform_sequence
    def get_ri_sequence(self):
        return self.ri_secuence
    
class NormalDistribution:
    def __init__(self, mean, stddev, seed, n):
        self.mean = mean
        self.stddev = stddev
        self.n = n
        self.seed = seed
        # generador de Ri congruencial lineal con parametros para generar minimo 1 millon de numeros
        self.lcg = LinealCongruence(xo_seed=self.seed, k=551757622, c=12345, g=31)
        self.ri_secuence = []

    # Genera los numeros Ni bajo una distribucion normal usando el metodo de Box-Muller
    def generate_normal(self):
        self.ri_secuence = self.lcg.generate_sequence(self.n * 2)  # Necesitamos el doble de numeros
        normal_sequence = []
        for i in range(0, len(self.ri_secuence), 2):
            u1 = max(min(self.ri_secuence[i], 1 - 1e-10), 1e-10)
            u2 = max(min(self.ri_secuence[i + 1], 1 - 1e-10), 1e-10)

            z0 = (-2 * math.log(u1)) ** 0.5 * math.cos(2 * math.pi * u2)
            z1 = (-2 * math.log(u1)) ** 0.5 * math.sin(2 * math.pi * u2)

            normal_sequence.append(self.mean + self.stddev * z0)
            if len(normal_sequence) < self.n:
                normal_sequence.append(self.mean + self.stddev * z1)

        return normal_sequence[:self.n]
    def get_ri_sequence(self):
        return self.ri_secuence

    