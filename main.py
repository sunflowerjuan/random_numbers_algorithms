from generators.congruences.Congruences import LinealCongruence

lcg = LinealCongruence(xo_seed=1,k=1, c=3, g=31)  # Ejemplo de inicialización

lcg.a=1103515245
lcg.c=12345


print("Hull-Dobell Validation:", lcg.hull_dobell_validation())

n = 10000
sequence = lcg.generate_sequence(n)
print(f"Generated sequence of {n} numbers:", sequence)