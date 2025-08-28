from LinealCongruence import LinealCongruence

lcg = LinealCongruence(seed=7, k=2, c=3, g=4)

print("Hull-Dobell Validation:", lcg.hull_dobell_validation())

n = 10
sequence = lcg.generate_sequence(n)
print(f"Generated sequence of {n} numbers:", sequence)