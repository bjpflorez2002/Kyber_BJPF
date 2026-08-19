n = 8
q = 17
zeta = 9

# precomputed zeta powers, same idea as real Kyber's zetas table, just for n=8.
# index 0 is unused (same as real code), indices 1..3 are what NTT actually uses.
zetas = [1, 13, 9, 15]

# gammas used by MultiplyNTTs - one per pair (n/2 = 4 pairs for n=8)
gammas = [9, 8, 15, 2]


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


def NTT(f):
    f_hat = f.copy()
    i = 1
    length = 4
    print("  starting NTT, f =", f)
    while length >= 2:
        start = 0
        while start < n:
            z = zetas[i]
            print(f"  stage length={length}, start={start}: using zeta={z}")
            i += 1
            for j in range(start, start + length):
                t = (z * f_hat[j + length]) % q
                before = (f_hat[j], f_hat[j + length])
                f_hat[j + length] = (f_hat[j] - t) % q
                f_hat[j] = (f_hat[j] + t) % q
                print(f"    butterfly j={j}: before={before}  ->  after=({f_hat[j]}, {f_hat[j+length]})")
            start += 2 * length
        length //= 2
    print("  finished NTT, f_hat =", f_hat)
    return f_hat


def NTT_inverse(f_hat):
    f = f_hat.copy()
    i = 3
    length = 2
    while length <= 4:
        start = 0
        while start < n:
            z = zetas[i]
            i -= 1
            for j in range(start, start + length):
                t = f[j]
                f[j] = (t + f[j + length]) % q
                f[j + length] = (z * (f[j + length] - t)) % q
            start += 2 * length
        length *= 2
    inverse_of_half_n = 13  # 4^-1 mod 17
    f = [(x * inverse_of_half_n) % q for x in f]
    return f


def base_case_multiply(a0, a1, b0, b1, gamma):
    c0 = (a0 * b0 + a1 * b1 * gamma) % q
    c1 = (a0 * b1 + a1 * b0) % q
    return c0, c1


def multiply_ntts(f_hat, g_hat):
    h_hat = [0] * n
    for i in range(4):
        c0, c1 = base_case_multiply(f_hat[2 * i], f_hat[2 * i + 1], g_hat[2 * i], g_hat[2 * i + 1], gammas[i])
        h_hat[2 * i] = c0
        h_hat[2 * i + 1] = c1
    return h_hat


f = [1, 2, 0, 1, 0, 0, 1, 0]
g = [2, 0, 1, 0, 1, 0, 0, 1]

print("=== schoolbook (the slow, already-known way) ===")
result_schoolbook = poly_mult_schoolbook(f, g)
print("result:", result_schoolbook)

print()
print("=== NTT way ===")
print("--- NTT(f) ---")
f_hat = NTT(f)
print()
print("--- NTT(g) ---")
g_hat = NTT(g)

print()
print("--- multiply_ntts(f_hat, g_hat) ---")
h_hat = multiply_ntts(f_hat, g_hat)
print("h_hat =", h_hat)

print()
print("--- NTT_inverse(h_hat) ---")
result_ntt = NTT_inverse(h_hat)
print("result:", result_ntt)

print()
print("MATCH:", result_schoolbook == result_ntt)
