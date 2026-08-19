import random

n = 256
q = 3329

# the real FIPS 203 zetas table (Appendix A) - zeta^BitRev7(i) mod q for i=0..127
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


def NTT_traced(f, label):
    f_hat = f.copy()
    i = 1
    length = 128
    round_num = 1
    print(f"=== Transforming {label} ===")
    while length >= 2:
        start = 0
        while start < n:
            z = zetas[i]
            print(f"--- Round {round_num}, magic number = {z}, pairing positions {length} apart ---")
            i += 1
            for j in range(start, start + length):
                a, b = f_hat[j], f_hat[j + length]
                t = (z * b) % q
                new_a = (a + t) % q
                new_b = (a - t) % q
                print(f"  pair(pos{j},pos{j+length}): ({a},{b})  t={z}x{b}mod{q}={t}  -> pos{j}={new_a}, pos{j+length}={new_b}")
                f_hat[j] = new_a
                f_hat[j + length] = new_b
            start += 2 * length
            round_num += 1
        length //= 2
    print(f"Finished {label}. Result: {f_hat}")
    print()
    return f_hat


def NTT_inverse_traced(f_hat):
    f = f_hat.copy()
    i = 127
    length = 2
    round_num = 1
    print("=== Transforming back ===")
    while length <= 128:
        start = 0
        while start < n:
            z = zetas[i]
            print(f"--- Reverse round {round_num}, magic number = {z} ---")
            i -= 1
            for j in range(start, start + length):
                a, b = f[j], f[j + length]
                new_a = (a + b) % q
                new_b = (z * (b - a)) % q
                print(f"  pair(pos{j},pos{j+length}): ({a},{b})  -> pos{j}={new_a}, pos{j+length}={new_b}")
                f[j] = new_a
                f[j + length] = new_b
            start += 2 * length
            round_num += 1
        length *= 2
    inv = 3303  # 128^-1 mod 3329
    print("Before final scaling:", f[:10], "...")
    f = [(x * inv) % q for x in f]
    print("After scaling by 3303:", f[:10], "...")
    print()
    return f


def base_case_multiply(a0, a1, b0, b1, gamma):
    c0 = (a0 * b0 + a1 * b1 * gamma) % q
    c1 = (a0 * b1 + a1 * b0) % q
    return c0, c1


def multiply_traced(f_hat, g_hat):
    h_hat = [0] * n
    print("=== Multiplying transformed lists ===")
    for i in range(128):
        a0, a1 = f_hat[2 * i], f_hat[2 * i + 1]
        b0, b1 = g_hat[2 * i], g_hat[2 * i + 1]
        gamma = zetas_mult[i]
        c0, c1 = base_case_multiply(a0, a1, b0, b1, gamma)
        print(f"  pair {i}: f=({a0},{a1}) g=({b0},{b1}) gamma={gamma}  -> ({c0},{c1})")
        h_hat[2 * i] = c0
        h_hat[2 * i + 1] = c1
    print()
    return h_hat


def poly_mult_schoolbook(f, g):
    raw = [0] * (2 * n - 1)
    for i in range(n):
        for j in range(n):
            raw[i + j] = (raw[i + j] + f[i] * g[j]) % q
    folded = [0] * n
    for i in range(n):
        folded[i] = raw[i]
    for i in range(n, 2 * n - 1):
        pos = i - n
        folded[pos] = (folded[pos] - raw[i]) % q
    return folded


random.seed(42)
f = [random.randint(0, q - 1) for _ in range(n)]
g = [random.randint(0, q - 1) for _ in range(n)]

print("f (first 10):", f[:10], "...")
print("g (first 10):", g[:10], "...")
print()

f_hat = NTT_traced(f, "f")
g_hat = NTT_traced(g, "g")
h_hat = multiply_traced(f_hat, g_hat)
result_ntt = NTT_inverse_traced(h_hat)

result_schoolbook = poly_mult_schoolbook(f, g)

print("=== FINAL CHECK ===")
print("schoolbook:", result_schoolbook[:10], "...")
print("NTT:       ", result_ntt[:10], "...")
print("MATCH:", result_schoolbook == result_ntt)
