import random

from toy_poly_kyber_3x3 import n, q, poly_mult


def reference_poly_mult(f, g):
    """
    Independent reference implementation, written differently on purpose:
    computes the exponent's sign and wrapped position using division/modulo
    directly, instead of the subtract-once approach in poly_mult.
    """
    raw = [0] * (2 * n - 1)
    for i in range(n):
        for j in range(n):
            raw[i + j] += f[i] * g[j]

    result = [0] * n
    for exponent in range(len(raw)):
        wraps = exponent // n          # how many times n fits into this exponent
        position = exponent % n        # where it lands after wrapping
        sign = (-1) ** wraps           # each full wrap flips the sign again
        result[position] += sign * raw[exponent]

    return [c % q for c in result]


random.seed(1)
trials = 2000
failures = 0
for t in range(trials):
    f = [random.randint(0, q - 1) for _ in range(n)]
    g = [random.randint(0, q - 1) for _ in range(n)]
    got = poly_mult(f, g)
    expected = reference_poly_mult(f, g)
    if got != expected:
        failures += 1
        if failures <= 5:
            print(f"MISMATCH: f={f} g={g} poly_mult={got} reference={expected}")

print(f"\n{trials - failures}/{trials} random trials matched the independent reference.")
