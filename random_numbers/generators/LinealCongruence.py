import math

from Congruences import Congruences

class LinealCongruence(Congruences):
    
    def __init__(self, xo_seed, k, c, g):
        super().__init__(xo_seed, g)
        self.a = 1 + 2 * k
        self.c = c
        
    # Genera la siguiente semilla y retorna un número Ri
    def next(self):
        # Toma la semilla actual y genera el siguiente número pseudoaleatorio
        self.xo_seed = (self.a * self.xo_seed + self.c) % self.m
        # Calcula Ri y lo retorna con 5 decimales
        ri=self.xo_seed / (self.m-1)
        ri_trucated =math.trunc(ri * 10**5) / 10**5
        return  ri_trucated
    

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
    

    
