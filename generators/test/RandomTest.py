from abc import ABC, abstractmethod
import numpy as np
from scipy.stats import kstwo, norm, chi2
from collections import Counter
import math

# Interfaz común para todas las pruebas
class RandomTest(ABC):
    def __init__(self, error=0.05):
        self.error = error

    @abstractmethod
    def run(self, sequence):
        pass

    def set_error(self, error):
        self.error = error
        
# Prueba de medias
class MeanTest(RandomTest):
    def run(self, sequence):
            mean = np.mean(sequence)
            n = len(sequence)

            # valor crítico para el intervalo (nivel de confianza = 1 - error)
            z_alpha = norm.ppf(1 - self.error/2)

            # cálculo de límites inferior y superior
            li = 0.5 - z_alpha * np.sqrt(1 / (12 * n))
            ls = 0.5 + z_alpha * np.sqrt(1 / (12 * n))

            # verificación si la media está dentro del intervalo
            passed = li <= mean <= ls
            return passed
    
# Prueba de Varianza
class VarianceTest(RandomTest):
    def run(self, sequence):
            n = len(sequence)
            var = np.var(sequence, ddof=1)  # varianza muestral (n-1)

            # valores críticos de chi-cuadrado
            chi2_lower = chi2.ppf(self.error / 2, n - 1)
            chi2_upper = chi2.ppf(1 - self.error / 2, n - 1)

            # límites inferior y superior
            li = chi2_lower / (12 * (n - 1))
            ls = chi2_upper / (12 * (n - 1))

            # verificación si la varianza cae dentro del intervalo
            passed = li <= var <= ls

            return passed
        
# Prueba de Chi-cuadrado
class ChiSquareTest(RandomTest):
     def run(self, sequence):
        n = len(sequence)

        # Número de intervalos ley Sturges
        k = int(1 + 3.322 * math.log10(n))
        # Límites de los intervalos
        intervals = np.linspace(0, 1, k + 1)
        # Contar frecuencias observadas
        fo, _ = np.histogram(sequence, bins=intervals)
        # Frecuencia esperada
        fe = n / k
        # Estadístico Chi2
        chi2_stat = np.sum((fo - fe) ** 2 / fe)
        # Valor crítico
        chi2_crit = chi2.ppf(1 - self.error, k - 1)

        # Pasó la prueba si chi2_stat < chi2_crit
        passed = chi2_stat < chi2_crit

        return passed

# Prueba de Kolmogorov-Smirnov
class KolmogorovSmirnovTest(RandomTest):
     def run(self, sequence):
        n = len(sequence)
        sequence = np.sort(sequence)

        # Distribución empírica F_n(x) = i/n
        fn = np.arange(1, n + 1) / n
        f_theoretical = sequence
        diffs = np.abs(fn - f_theoretical)

        # Estadístico D
        d_max = np.max(diffs)

        # Valor crítico según n
        if n > 35:
            c_alpha = {0.10: 1.22, 0.05: 1.36, 0.01: 1.63}
            c = c_alpha.get(self.error, 1.36)
            d_alpha = c / np.sqrt(n)
        else:
            # Valor con distribución KS
            d_alpha = kstwo.ppf(1 - self.error, n) / n

        passed = d_max < d_alpha

        return passed




# Prueba de Poker (simplificada)
class PokerTest(RandomTest):
       def run(self, sequence):
        n = len(sequence)

        # categorías y probabilidades teóricas
        categories = ["Diferentes", "Un par", "Dos pares", "Tercia", "Full", "Poker", "Quintilla"]
        probs = [0.3024, 0.5040, 0.1080, 0.0720, 0.0090, 0.0045, 0.0001]

        observed = np.zeros(len(categories))

        for ri in sequence:
            # tomar 5 dígitos significativos y rellenar con ceros si faltan
            digits = str(ri)[2:7].ljust(5, "0")

            # contar ocurrencias de dígitos
            counts = sorted(Counter(digits).values(), reverse=True)

            # clasificación según el patrón
            if counts == [5]:
                observed[6] += 1  # Quintilla
            elif counts == [4, 1]:
                observed[5] += 1  # Poker
            elif counts == [3, 2]:
                observed[4] += 1  # Full
            elif counts == [3, 1, 1]:
                observed[3] += 1  # Tercia
            elif counts == [2, 2, 1]:
                observed[2] += 1  # Dos pares
            elif counts == [2, 1, 1, 1]:
                observed[1] += 1  # Un par
            else:
                observed[0] += 1  # diferentes

        # esperados
        expected = np.array(probs) * n

        # chi-cuadrado
        chi2_stat = np.sum((observed - expected) ** 2 / expected)
        gl = len(categories) - 1
        chi2_crit = chi2.ppf(1 - self.error, gl)

        passed = chi2_stat < chi2_crit

        return passed

# Prueba de Corridas (Runs)
class RunsTest(RandomTest):
    def run(self, sequence):
        median = np.median(sequence)
        runs, n1, n2 = 1, 0, 0
        prev = sequence[0] > median
        for x in sequence[1:]:
            curr = x > median
            if curr != prev:
                runs += 1
            prev = curr
            if curr:
                n1 += 1
            else:
                n2 += 1
        expected_runs = ((2 * n1 * n2) / (n1 + n2)) + 1
        std_runs = np.sqrt((2 * n1 * n2 * (2 * n1 * n2 - n1 - n2)) / (((n1 + n2) ** 2) * (n1 + n2 - 1)))
        z = (runs - expected_runs) / std_runs if std_runs > 0 else 0
        from scipy.stats import norm
        p = 2 * (1 - norm.cdf(abs(z)))
        passed=p > self.error
        return passed



# Fachada para ejecutar todas las pruebas
from abc import ABC, abstractmethod
import numpy as np
from scipy.stats import kstwo, norm, chi2
from collections import Counter
import math

# Interfaz común para todas las pruebas
class RandomTest(ABC):
    def __init__(self, error=0.05):
        self.error = error

    @abstractmethod
    def run(self, sequence):
        pass

    def set_error(self, error):
        self.error = error


# ------------------------------
# PRUEBAS
# ------------------------------

# 1. Prueba de medias
class MeanTest(RandomTest):
    def run(self, sequence):
        mean = np.mean(sequence)
        n = len(sequence)

        z_alpha = norm.ppf(1 - self.error/2)
        li = 0.5 - z_alpha * np.sqrt(1 / (12 * n))
        ls = 0.5 + z_alpha * np.sqrt(1 / (12 * n))

        passed = li <= mean <= ls
        return passed, mean, (li, ls)


# 2. Prueba de Varianza
class VarianceTest(RandomTest):
    def run(self, sequence):
        n = len(sequence)
        var = np.var(sequence, ddof=1)

        chi2_lower = chi2.ppf(self.error / 2, n - 1)
        chi2_upper = chi2.ppf(1 - self.error / 2, n - 1)

        li = chi2_lower / (12 * (n - 1))
        ls = chi2_upper / (12 * (n - 1))

        passed = li <= var <= ls
        return passed, var, (li, ls)


# 3. Prueba de Chi-cuadrado (Sturges)
class ChiSquareTest(RandomTest):
    def run(self, sequence):
        n = len(sequence)
        k = int(1 + 3.322 * math.log10(n))
        intervals = np.linspace(0, 1, k + 1)
        fo, _ = np.histogram(sequence, bins=intervals)
        fe = n / k
        chi2_stat = np.sum((fo - fe) ** 2 / fe)
        chi2_crit = chi2.ppf(1 - self.error, k - 1)
        passed = chi2_stat < chi2_crit
        return passed, chi2_stat, chi2_crit


# 4. Prueba de Kolmogorov-Smirnov con Sturges
class KolmogorovSmirnovTest(RandomTest):
    def run(self, sequence):
        n = len(sequence)

        # Número de intervalos (Sturges)
        k = int(1 + 3.322 * math.log10(n))
        intervals = np.linspace(min(sequence), max(sequence), k + 1)

        # Frecuencias observadas
        fo, _ = np.histogram(sequence, bins=intervals)

        # Frecuencia acumulada observada
        fo_acum = np.cumsum(fo) / n

        # Frecuencia acumulada esperada (uniforme)
        fe = np.full(k, n / k)
        fe_acum = np.cumsum(fe) / n

        # Estadístico KS agrupado
        d_max = np.max(np.abs(fe_acum-fo_acum))

        # Valor crítico de KS 
        d_alpha = kstwo.ppf(1 - self.error, n)


        passed = d_max < d_alpha
        return passed, d_max, d_alpha


# 5. Prueba de Poker
class PokerTest(RandomTest):
    def run(self, sequence):
        n = len(sequence)
        categories = ["Diferentes", "Un par", "Dos pares", "Tercia", "Full", "Poker", "Quintilla"]
        probs = [0.3024, 0.5040, 0.1080, 0.0720, 0.0090, 0.0045, 0.0001]
        observed = np.zeros(len(categories))

        for ri in sequence:
            digits = str(ri)[2:7].ljust(5, "0")
            counts = sorted(Counter(digits).values(), reverse=True)
            if counts == [5]:
                observed[6] += 1
            elif counts == [4, 1]:
                observed[5] += 1
            elif counts == [3, 2]:
                observed[4] += 1
            elif counts == [3, 1, 1]:
                observed[3] += 1
            elif counts == [2, 2, 1]:
                observed[2] += 1
            elif counts == [2, 1, 1, 1]:
                observed[1] += 1
            else:
                observed[0] += 1

        expected = np.array(probs) * n
        chi2_stat = np.sum((observed - expected) ** 2 / expected)
        gl = len(categories) - 1
        chi2_crit = chi2.ppf(1 - self.error, gl)
        passed = chi2_stat < chi2_crit


        return passed, observed.tolist(), expected.tolist()




# 6. Prueba de Corridas (Runs)
class RunsTest(RandomTest):
    def run(self, sequence):
        median = np.median(sequence)
        runs, n1, n2 = 1, 0, 0
        prev = sequence[0] > median
        for x in sequence[1:]:
            curr = x > median
            if curr != prev:
                runs += 1
            prev = curr
            if curr:
                n1 += 1
            else:
                n2 += 1

        expected_runs = ((2 * n1 * n2) / (n1 + n2)) + 1
        std_runs = np.sqrt((2 * n1 * n2 * (2 * n1 * n2 - n1 - n2)) /
                           (((n1 + n2) ** 2) * (n1 + n2 - 1)))
        z = (runs - expected_runs) / std_runs if std_runs > 0 else 0
        p = 2 * (1 - norm.cdf(abs(z)))
        passed = p > self.error
        return passed, z, p


# ------------------------------
# FACHADA
# ------------------------------
class RandomTestFacade:
    def __init__(self, error=0.05):
        self.error = error
        self.tests = [
            MeanTest(error),
            VarianceTest(error),
            ChiSquareTest(error),
            KolmogorovSmirnovTest(error),
            PokerTest(error),
            RunsTest(error)
        ]
        self.test_names = [
            "Mean",
            "Variance",
            "Chi-Square",
            "Kolmogorov-Smirnov",
            "Poker",
            "Runs"
        ]

    def set_error(self, error):
        self.error = error
        for test in self.tests:
            test.set_error(error)

    def run_all(self, sequence):
        results = {}
        overall_passed = True
        for name, test in zip(self.test_names, self.tests):
            passed, stat, crit = test.run(sequence)
            if not passed:
                overall_passed = False
            results[name] = {
                "passed": "PASA" if passed else "NO PASA",
                "statistic": stat,
                "p_value_or_threshold": crit
            }
        return results, overall_passed



