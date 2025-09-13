
from generators.Congruences import LinealCongruence

class UniformDistribution:
    def __init__(self, seed, n,a,b):
        self.n = n
        self.seed = seed
        self.a = a
        self.b = b
        # generador de Ri congruencial lineal con parametros para generar minimo 1 millon de numeros
        self.lcg = LinealCongruence(xo_seed=self.seed, k=551757622, c=12345, g=31)

    # Genera los numeros Ni bajo una distribucion uniforme
    def generate_uniform(self):
        sequence = self.lcg.generate_sequence(self.n)
        # secuencia de numeros uniformes con la formula de transformacion a Ni
        uniform_sequence = [self.a + (self.b - self.a) * r for r in sequence]
        return uniform_sequence
    