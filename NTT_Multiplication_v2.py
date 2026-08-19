import random

n = 256
q = 3329

# zeta - the 128 magic numbers straight from FIPS 203 Appendix A. we didnt
# calculate these, theyre just given to us, same idea as CBD_TABLE was.
# used by hat_maker, walked through in plain order (index 1, then 2, then 3...)
zeta = [
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

# zeta_reverse - literally zeta flipped end to end, so NTT_final can just walk
# forward through it instead of walking zeta backwards. same 127 numbers,
# just read from the other end (index 127 first, down to index 1 last).
zeta_reverse = list(reversed(zeta[1:128]))

# gamma - a SEPARATE table of 128 numbers, also straight from FIPS 203
# Appendix A, used only in c_hat_maker (the multiply step), one per pair.
gamma = [
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


# hat_maker - turns a normal 256-number poly into its transformed (hat) shape.
# 7 rounds, pairing distance halves each round (128,64,32,...,2), every group
# just grabs the next zeta in line. this is the forward direction.
def hat_maker(f):
    f_hat = f.copy()
    i = 1
    length = 128
    while length >= 2:
        start = 0
        while start < n:
            z = zeta[i]
            i += 1
            for j in range(start, start + length):
                t = (z * f_hat[j + length]) % q
                f_hat[j + length] = (f_hat[j] - t) % q
                f_hat[j] = (f_hat[j] + t) % q
            start += 2 * length
        length //= 2
    return f_hat


# NTT_final - undoes hat_maker. same idea backwards: rounds go 2,4,8...128,
# reads zeta_reverse forward instead of zeta backward, and the formula itself
# flips (add first, then multiply). one last scaling step at the very end
# cleans up a leftover factor left behind by doing 7 rounds.
def NTT_final(c_hat):
    f = c_hat.copy()
    i = 0
    length = 2
    while length <= 128:
        start = 0
        while start < n:
            z = zeta_reverse[i]
            i += 1
            for j in range(start, start + length):
                t = f[j]
                f[j] = (t + f[j + length]) % q
                f[j + length] = (z * (f[j + length] - t)) % q
            start += 2 * length
        length *= 2
    inverse_of_half_n = 3303  # cancels out the leftover factor from 7 rounds
    f = [(x * inverse_of_half_n) % q for x in f]
    return f


# c_hat_coefficient - handles just ONE pair during the multiply step. takes
# one pair from f_hat, one matching pair from g_hat, and that pairs own
# gamma, and hands back the 2 new numbers for that pair.
def c_hat_coefficient(a0, a1, b0, b1, gamma_value):
    c0 = (a0 * b0 + a1 * b1 * gamma_value) % q
    c1 = (a0 * b1 + a1 * b0) % q
    return c0, c1


# c_hat_maker - loops through all 128 pairs, calling c_hat_coefficient on
# each one, and builds the full 256-number c_hat list from the results.
def c_hat_maker(f_hat, g_hat):
    c_hat = [0] * n
    for i in range(128):
        c0, c1 = c_hat_coefficient(f_hat[2 * i], f_hat[2 * i + 1], g_hat[2 * i], g_hat[2 * i + 1], gamma[i])
        c_hat[2 * i] = c0
        c_hat[2 * i + 1] = c1
    return c_hat


# poly_mult_schoolbook - has nothing to do with the NTT process. this is just
# the old slow multiply, kept around purely to check the NTT answer against.
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

f_hat = hat_maker(f)
g_hat = hat_maker(g)
c_hat = c_hat_maker(f_hat, g_hat)
result_ntt = NTT_final(c_hat)

result_schoolbook = poly_mult_schoolbook(f, g)

print("f (first 5):", f[:5])
print("g (first 5):", g[:5])
print()
print("f_hat (first 5):", f_hat[:5])
print("g_hat (first 5):", g_hat[:5])
print()
print("c_hat (first 5):", c_hat[:5])
print()
print("schoolbook result (first 5):", result_schoolbook[:5])
print("NTT result (first 5):       ", result_ntt[:5])
print()
print("MATCH:", result_schoolbook == result_ntt)
