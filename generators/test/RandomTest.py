from abc import ABC, abstractmethod
import numpy as np
from scipy.stats import norm, chi2
from collections import Counter
import math


# Interfaz común
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

        z_alpha = norm.ppf(1 - self.error / 2)
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
        k = int(1 + 3.322 * math.log10(n))  # Regla de Sturges
        intervals = np.linspace(0, 1, k + 1)
        fo, _ = np.histogram(sequence, bins=intervals)
        fe = np.full(k, n / k)  # vector con la frecuencia esperada en cada intervalo
        chi2_stat = np.sum((fo - fe) ** 2 / fe)
        chi2_crit = chi2.ppf(1 - self.error, k - 1)

        passed = chi2_stat < chi2_crit
        return passed, chi2_stat, {
            "chi2_crit": chi2_crit,
            "fo": fo.tolist(),
            "fe": fe.tolist(),
            "k": k
        }


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
        d_max = np.max(np.abs(fe_acum - fo_acum))

        # Valor crítico de KS
        d_alpha = 1.36 / np.sqrt(n)  # constante aprox. para alfa=0.05
        # si quieres exactitud usa: kstwo.ppf(1 - self.error, n)

        passed = d_max < d_alpha
        return passed, d_max, d_alpha


# 5. Prueba de Poker
class PokerTest(RandomTest):
    def run(self, sequence):
        n = len(sequence)
        # Listas de categorías y sus probabilidades
        categories = ["Diferentes", "Un par", "Dos pares", "Tercia", "Full", "Poker", "Quintilla"]
        probs = [0.3024, 0.5040, 0.1080, 0.0720, 0.0090, 0.0045, 0.0001]
        
        observed = np.zeros(len(categories))

        #contar ocurrencias
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
                
        # Estadístico Chi-cuadrado
        expected = np.array(probs) * n
        
        # Observado y esperado
        chi2_stat = np.sum((observed - expected) ** 2 / expected)
        # Grados de libertad y valor crítico
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

        # Estadístico Z
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
    
    # Actualizar el nivel de significancia para todas las pruebas
    def set_error(self, error):
        self.error = error
        for test in self.tests:
            test.set_error(error)

    # Ejecutar todas las pruebas
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
    
    # Ejecutar un subconjunto de pruebas
    def run_subset(self, sequence, chosen_tests):
        all_results, _ = self.run_all(sequence)
        # filtrar solo las pruebas seleccionadas
        results = {name: res for name, res in all_results.items() if name in chosen_tests}
        overall_passed = all(res["passed"] == "PASA" for res in results.values())
        return results, overall_passed
