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
    
    # Valida si los parametros cumplen con el teorema de Hull-Dobell
    @abstractmethod
    def hull_dobell_validation(self):
        pass
    
    
    # Genera la secuencia de numeros pseudoaleatorios Ri con un parametro n (Tamaño de la secuencia)
    def generate_sequence(self, n):
        sequence = []
        for _ in range(n):
            sequence.append(self.next())
        return sequence
    
    # Calcula el periodo del generador

   

# Clase congruencia Lineal
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
    
    # Método auxiliar: calcula la siguiente semilla SIN alterar xo_seed
    def _next_seed(self, seed):
        return (self.a * seed + self.c) % self.m 
    
    

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
  
         
    # Detecta el período con Floyd, limitado por max_steps.
    # Si Hull-Dobell se cumple, devuelve m directamente.
    # Si no cumple y se exceden max_steps, devuelve un estimado.
        
    def get_period(self, max_steps=10**6):
        if self.hull_dobell_validation():
            return self.m  # periodo máximo garantizado
        start_seed = self.xo_seed
        tortoise = self._next_seed(start_seed)
        hare = self._next_seed(self._next_seed(start_seed))

        steps = 0
        while tortoise != hare and steps < max_steps:
            tortoise = self._next_seed(tortoise)
            hare = self._next_seed(self._next_seed(hare))
            steps += 1

        if steps >= max_steps:
            # En vez de devolver un string, devolvemos el límite como int
            return max_steps

        # Colisión → calcular periodo exacto
        mu = 0
        tortoise = start_seed
        while tortoise != hare:
            tortoise = self._next_seed(tortoise)
            hare = self._next_seed(hare)
            mu += 1

        lam = 1
        hare = self._next_seed(tortoise)
        while tortoise != hare:
            hare = self._next_seed(hare)
            lam += 1

        return lam

    
# Clase de congruencia Aditiva
class AditiveCongruence(LinealCongruence):
    
    def __init__(self, xo_seed,c, g):
        super().__init__(xo_seed,0, c, g)
       
   
    #Valida si los parametros cumplen con el teorema de Hull-Dobell aditive=o
    def hull_dobell_validation(self):
        #verifica que c y m sean primos relativos
        import math
        return math.gcd(self.c, self.m) == 1

# Clase de congruencia multiplicativa
class MultipyCongruence(LinealCongruence):
    
    def __init__(self, xo_seed,k, g):
        super().__init__(xo_seed, k, 0, g)    
    
    #Valida si los parametros cumplen con el teorema de Hull-Dobell aditive=o
    def hull_dobell_validation(self):
         # a % 8 == 3 for m = 2^g
        return self.a % 8 == 3

    
