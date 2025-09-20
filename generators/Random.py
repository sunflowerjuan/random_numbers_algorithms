"""
Random — envoltura (facade) para generación de números pseudoaleatorios.

Resumen rápido:
- Esta clase centraliza generación de Ri con un LCG (LinealCongruence),
  transformaciones a distribuciones (uniforme y normal) y validación
  estadística de las secuencias con RandomTestFacade.
- La semilla se genera dinámicamente en cada llamada usando time.time_ns(),
  por eso cada llamada produce secuencias distintas.
- Si una secuencia no pasa las pruebas estadísticas, se regenera con otra semilla
  hasta que pase (ten cuidado con bucles infinitos / rendimiento).
"""

import time
import math
from generators.Congruences import LinealCongruence
from distributions.Distributions import UniformDistribution, NormalDistribution
from generators.test.RandomTest import RandomTestFacade


class Random:
    """
    Clase Random: interfaz para generar números Ri y transformarlos a
    distribuciones (uniforme, normal) con validación estadística.

    Parámetros del constructor:
      - error (float): nivel de significancia usado por RandomTestFacade.
                       Por defecto 0.05 (5%). Valores menores = pruebas más estrictas.
      - deterministic (bool): controla el modo de generación de semilla.
            * True  → modo determinista: se genera UNA sola semilla al crear el objeto
              y se reutiliza en todas las llamadas NO SE SI LO NECESITEN PERO AHI ESTA.
            * False → modo dinámico: en cada llamada se genera una semilla distinta
              basada en time.time_ns() hora exacta con nanosegundos (por defecto, comportamiento no repetible).
    Atributos privados:
      - self._fixed_seed: almacena la semilla fija en modo determinista.
    """
    def __init__(self, error=0.05, deterministic=False):
        self.error = error
        self.facade = RandomTestFacade(error)

        self.deterministic = deterministic
        self._fixed_seed = None

        if deterministic:
            # Guardamos una semilla fija para todo el ciclo de vida del objeto
            self._fixed_seed = int(time.time_ns() % (2**31 - 1))

    # ----------------------------
    # 0. Gestión de la semilla
    # ----------------------------
    def _get_seed(self,failed_test=False):
        """
        Devuelve la semilla a usar:
          - Si deterministic=True → devuelve la misma semilla cada vez.
          - Si deterministic=False → devuelve una semilla dinámica basada en time.time_ns().
          - Si failed_test=True (llamado tras fallo de test), fuerza semilla dinámica
        """
        # Si se llama desde un fallo de test, forzamos semilla dinámica
        if failed_test:
            return int(time.time_ns() % (2**31 - 1))
        if self.deterministic and self._fixed_seed is not None:
            return self._fixed_seed
        return int(time.time_ns() % (2**31 - 1))
    
    
    # ----------------------------
    # 1. Generación base de Ri
    # ----------------------------
    def random(self, n=None):
        """
        Genera Ri con el LCG.

        Parámetros:
          - n (int or None):
              * None (por defecto) -> devuelve un único Ri (float en [0,1)).
              * entero > 0 -> devuelve una lista de n Ri.
        Comportamiento:
          - La semilla depende del modo (determinista o dinámico).
          - Si se pide una secuencia, se valida con RandomTestFacade. Si falla, se regenera.
          - Si se pide un solo Ri, se devuelve directamente sin validación.
        """
        seed = self._get_seed()
        lcg = LinealCongruence(xo_seed=seed, k=551757622, c=12345, g=31)

        if n is None:
            return lcg.next()
        else:
            sequence = lcg.generate_sequence(n)
            while not self._validate_sequence(sequence):
                seed = self._get_seed(failed_test=True)
                lcg = LinealCongruence(xo_seed=seed, k=551757622, c=12345, g=31)
                sequence = lcg.generate_sequence(n)
            return sequence


    # ----------------------------
    # 2. Distribución uniforme
    # ----------------------------
    def uniform(self, a, b, n=None, integer=False):
        """
        Genera números bajo una distribución uniforme en [a, b].

        Parámetros:
          - a (float/int): límite inferior.
          - b (float/int): límite superior.
          - n (int or None): cantidad de valores (None -> un solo valor).
          - integer (bool): si True → devuelve enteros truncados, si False → floats.
        """
        seed = self._get_seed()

        if n is None:
            u = UniformDistribution(seed, 1, a, b)
            seq = u.generate_uniform()
            value = seq[0]
            return int(math.trunc(value)) if integer else value
        else:
            u = UniformDistribution(seed, n, a, b)
            seq = u.generate_uniform()
            while not self._validate_sequence(u.get_ri_sequence()):
                seed = self._get_seed(failed_test=True)
                u = UniformDistribution(seed, n, a, b)
                seq = u.generate_uniform()
            return [int(math.trunc(x)) for x in seq] if integer else seq

    # ----------------------------
    # 3. Distribución normal
    # ----------------------------
    def normal(self, mean, stddev, n=None):
        """
        Genera números bajo una distribución normal.

        Parámetros:
          - mean (float): media.
          - stddev (float): desviación estándar.
          - n (int or None): cantidad de valores. None -> devuelve un único valor.
        """
        seed = self._get_seed()
        if n is None:
            normal_d = NormalDistribution(mean, stddev, seed, 1)
            seq = normal_d.generate_normal()
            return seq[0]
        else:
            normal_d = NormalDistribution(mean, stddev, seed, n)
            seq = normal_d.generate_normal()
            while not self._validate_sequence(normal_d.get_ri_sequence()):
                seed = self._get_seed(failed_test=True)
                normal_d = NormalDistribution(mean, stddev, seed, n)
                seq = normal_d.generate_normal()
            return seq[0] if n == 1 else seq

    # ----------------------------
    # 4. Métodos auxiliares
    # ----------------------------
    def _validate_sequence(self, seq):
        """
        Ejecuta la lista de pruebas sobre la secuencia uniforme 'seq'.

        Retorna:
          - results (dict), passed (bool) desde RandomTestFacade.run_all(seq)
        Comportamiento actual: sólo devuelve el booleano 'passed' el valor de results se obtiene debido a
        que se retorna pero no le damos ningun uso 
        POR FAVOR NO QUITARLO o el metodo falla.
        """
        results, passed = self.facade.run_all(seq)

        return passed

    # ----------------------------
    # 5. Extras
    # ----------------------------

    def choice(self, seq):
        """
        Elige un elemento aleatorio de la lista 'seq' si quieres usar un solo valor de un numero pseudoaleatorio pero
        que este validado puedes utilizar este metodo en conjunto con una secuencia generada con cualquiera de los metodos
        anteriores.
        """
        # Implementación 
        idx = int(self.uniform(0, len(seq)))
        # Para evitar IndexError con la implementación actual
        if idx >= len(seq):
            idx = len(seq) - 1
        return seq[idx]


