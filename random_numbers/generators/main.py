from LinealCongruence import LinealCongruence

lcg = LinealCongruence(seed=5, k=3, c=7, g=5)

print("Hull-Dobell Validation:", lcg.hull_dobell_validation())

n = 10
sequence = lcg.generate_sequence(n)
print(f"Generated sequence of {n} numbers:", sequence)