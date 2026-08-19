import random
from Hashing_kyber_CBD_V2 import n, q, poly_add, poly_mult

# zetas: zeta^BitRev7(i) mod q for i = 0..127, straight from FIPS 203 Appendix A.
# used by NTT() and NTT_inverse().
zetas = [
    1, 1729, 2580, 3289, 2642, 630, 1897, 848,
    1062, 1919, 193, 797, 2786, 3260, 569, 1746,
    296, 2447, 1339, 1476, 3046, 56, 2240, 1333,
    1426, 2094, 535, 2882, 2393, 2879, 1974, 821,
    289, 331, 3253, 1756, 1197, 2304, 2277, 2055,
    650, 1977, 2513, 632, 2865, 33, 1320, 1915,
    2319, 1435, 807, 452, 1438, 2868, 1534, 2402,
    2647, 2617, 1481, 648, 2474, 3110, 1227, 910,
    17, 2761, 583, 2649, 1637, 723, 2288, 1100,
    1409, 2662, 3281, 233, 756, 2156, 3015, 3050,
    1703, 1651, 2789, 1789, 1847, 952, 1461, 2687,
    939, 2308, 2437, 2388, 733, 2337, 268, 641,
    1584, 2298, 2037, 3220, 375, 2549, 2090, 1645,
    1063, 319, 2773, 757, 2099, 561, 2466, 2594,
    2804, 1092, 403, 1026, 1143, 2150, 2775, 886,
    1722, 1212, 1874, 1029, 2110, 2935, 885, 2154,
]

# zetas_mult: zeta^(2*BitRev7(i)+1) mod q for i = 0..127, straight from
# FIPS 203 Appendix A. used by MultiplyNTTs() as the "gamma" for each pair.
zetas_mult = [
    17, -17, 2761, -2761, 583, -583, 2649, -2649,
    1637, -1637, 723, -723, 2288, -2288, 1100, -1100,
    1409, -1409, 2662, -2662, 3281, -3281, 233, -233,
    756, -756, 2156, -2156, 3015, -3015, 3050, -3050,
    1703, -1703, 1651, -1651, 2789, -2789, 1789, -1789,
    1847, -1847, 952, -952, 1461, -1461, 2687, -2687,
    939, -939, 2308, -2308, 2437, -2437, 2388, -2388,
    733, -733, 2337, -2337, 268, -268, 641, -641,
    1584, -1584, 2298, -2298, 2037, -2037, 3220, -3220,
    375, -375, 2549, -2549, 2090, -2090, 1645, -1645,
    1063, -1063, 319, -319, 2773, -2773, 757, -757,
    2099, -2099, 561, -561, 2466, -2466, 2594, -2594,
    2804, -2804, 1092, -1092, 403, -403, 1026, -1026,
    1143, -1143, 2150, -2150, 2775, -2775, 886, -886,
    1722, -1722, 1212, -1212, 1874, -1874, 1029, -1029,
    2110, -2110, 2935, -2935, 885, -885, 2154, -2154,
]


# NTT: Algorithm 9 from FIPS 203, followed exactly. Takes a normal
# 256-coefficient polynomial and returns its NTT representation.
def NTT(f):
    f_hat = f.copy()
    i = 1
    length = 128
    while length >= 2:
        start = 0
        while start < 256:
            zeta = zetas[i]
            i += 1
            for j in range(start, start + length):
                t = (zeta * f_hat[j + length]) % q
                f_hat[j + length] = (f_hat[j] - t) % q
                f_hat[j] = (f_hat[j] + t) % q
            start += 2 * length
        length //= 2
    return f_hat


# NTT_inverse: Algorithm 10 from FIPS 203, followed exactly. Undoes NTT(),
# converting an NTT representation back into a normal polynomial.
def NTT_inverse(f_hat):
    f = f_hat.copy()
    i = 127
    length = 2
    while length <= 128:
        start = 0
        while start < 256:
            zeta = zetas[i]
            i -= 1
            for j in range(start, start + length):
                t = f[j]
                f[j] = (t + f[j + length]) % q
                f[j + length] = (zeta * (f[j + length] - t)) % q
            start += 2 * length
        length *= 2
    f = [(x * 3303) % q for x in f]
    return f


# BaseCaseMultiply: Algorithm 12 from FIPS 203. Multiplies two degree-one
# polynomials with respect to a quadratic modulus (X^2 - gamma).
def base_case_multiply(a0, a1, b0, b1, gamma):
    c0 = (a0 * b0 + a1 * b1 * gamma) % q
    c1 = (a0 * b1 + a1 * b0) % q
    return c0, c1


# MultiplyNTTs: Algorithm 11 from FIPS 203. Multiplies two NTT
# representations together, 128 small pairwise multiplications at a time.
def multiply_ntts(f_hat, g_hat):
    h_hat = [0] * n
    for i in range(128):
        c0, c1 = base_case_multiply(
            f_hat[2 * i], f_hat[2 * i + 1],
            g_hat[2 * i], g_hat[2 * i + 1],
            zetas_mult[i],
        )
        h_hat[2 * i] = c0
        h_hat[2 * i + 1] = c1
    return h_hat


# --- test: multiply two random polynomials both ways, confirm they match ---
f = [random.randint(0, q - 1) for _ in range(n)]
g = [random.randint(0, q - 1) for _ in range(n)]

result_schoolbook = poly_mult(f, g)

f_hat = NTT(f)
g_hat = NTT(g)
h_hat = multiply_ntts(f_hat, g_hat)
result_ntt = NTT_inverse(h_hat)

print("schoolbook and NTT results match:", result_schoolbook == result_ntt)
print()
print("first 5 coefficients, schoolbook:", result_schoolbook[:5])
print("first 5 coefficients, NTT method:", result_ntt[:5])
