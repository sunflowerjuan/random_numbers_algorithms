import math

from decimal import Decimal, ROUND_DOWN

class LinealCongruence:
    def __init__(self, seed, k, c, g):
        self.seed = seed
        self.a = 1+2*k
        self.c = c
        self.m = int(math.pow(2, g))
        print ("m:", self.m)
        
    # Genera la siguiente semilla y retorna un número Ri
    def next(self):
        # Toma la semilla actual y genera el siguiente número pseudoaleatorio
        self.seed = (self.a * self.seed + self.c) % self.m
        print(f"Next seed: {self.seed}")
        # Calcula Ri y lo retorna con 5 decimales
        ri=Decimal(self.seed / (self.m-1))
        return  ri.quantize(Decimal("0.00001"), rounding=ROUND_DOWN)
    
    # Genera la secuencia de numeros pseudoaleatorios Ri con un parametro n (Tamaño de la secuencia)
    def generate_sequence(self, n):
        sequence = []
        for _ in range(n):
            sequence.append(self.next())
        return sequence
    
    # Valida si los parametros cumplen con el teorema de Hull-Dobell
    def hull_dobell_validation(self):
        # 1. c y m primos relativos
        cond1 = math.gcd(self.c, self.m) == 1

        # 2. a-1 divisible por todos los factores primos de m
        a_minus_1 = self.a - 1
        m_temp = self.m
        prime_factors = set()
        i = 2
        while i * i <= m_temp:
            if m_temp % i == 0:
                prime_factors.add(i)
                while m_temp % i == 0:
                    m_temp //= i
            i += 1
        if m_temp > 1:
            prime_factors.add(m_temp)
        cond2 = all(a_minus_1 % p == 0 for p in prime_factors)

        # 3. Si m divisible por 4, a-1 divisible por 4
        cond3 = True
        if self.m % 4 == 0:
            cond3 = a_minus_1 % 4 == 0

        return cond1 and cond2 and cond3
    
