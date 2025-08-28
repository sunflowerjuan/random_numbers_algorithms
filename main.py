from generators.congruences.Congruences import AditiveCongruence

lcg = AditiveCongruence(xo_seed=5, c=3, g=5)  # Ejemplo de inicialización

print("Hull-Dobell Validation:", lcg.hull_dobell_validation())

n = 10
sequence = lcg.generate_sequence(n)
print(f"Generated sequence of {n} numbers:", sequence)