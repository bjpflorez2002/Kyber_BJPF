n = 8
q = 17
zeta = 9

# same small table as before - index 0 unused, 1..3 are the magic numbers
# actually used, in the order the algorithm needs them (not simple 1,2,3 order)
zetas = [1, 13, 9, 15]
gammas = [9, 8, 15, 2]


def explained_butterfly(values, j, length, z):
    """Does one butterfly AND prints out, in plain words, what just happened."""
    a = values[j]
    b = values[j + length]
    print(f"  Taking the pair at position {j} (value {a}) and position {j+length} (value {b}).")

    t = (z * b) % q
    print(f"  Multiply the magic number ({z}) by the second value ({b}): {z} x {b} = {z*b}, which mod {q} is {t}.")

    new_a = (a + t) % q
    print(f"  Add that ({t}) to the first value ({a}): {a} + {t} = {a+t}, mod {q} is {new_a}. This is the new position {j}.")

    new_b = (a - t) % q
    print(f"  Subtract that ({t}) from the first value ({a}) instead: {a} - {t} = {a-t}, mod {q} is {new_b}. This is the new position {j+length}.")

    values[j] = new_a
    values[j + length] = new_b
    print()


def NTT_explained(f, label):
    print(f"=== Transforming {label} = {f} ===")
    print()
    f_hat = f.copy()
    i = 1
    length = 4
    round_number = 1
    while length >= 2:
        start = 0
        while start < n:
            z = zetas[i]
            print(f"--- Round {round_number}, using magic number {z}, pairing positions {length} apart ---")
            i += 1
            for j in range(start, start + length):
                explained_butterfly(f_hat, j, length, z)
            start += 2 * length
            round_number += 1
        length //= 2
    print(f"Finished transforming {label}. Result: {f_hat}")
    print()
    return f_hat


def NTT_inverse_explained(f_hat):
    print("=== Transforming back (undoing the process) ===")
    print()
    f = f_hat.copy()
    i = 3
    length = 2
    round_number = 1
    while length <= 4:
        start = 0
        while start < n:
            z = zetas[i]
            print(f"--- Reverse round {round_number}, using magic number {z} ---")
            i -= 1
            for j in range(start, start + length):
                a = f[j]
                b = f[j + length]
                new_a = (a + b) % q
                print(f"  Position {j} (value {a}) and position {j+length} (value {b}): add them together -> {a}+{b}={a+b}, mod {q} is {new_a}. New position {j}.")
                new_b = (z * (b - a)) % q
                print(f"  Take the second value minus the first ({b}-{a}={b-a}), multiply by the magic number {z}: {z}x{b-a}={z*(b-a)}, mod {q} is {new_b}. New position {j+length}.")
                print()
                f[j] = new_a
                f[j + length] = new_b
            start += 2 * length
            round_number += 1
        length *= 2

    print("Before the final scaling step:", f)
    scale = 13  # 4^-1 mod 17, the number that cancels out a leftover factor of 4
    print(f"Multiply every single number by {scale} (this cancels out a leftover factor of 4 from the transform):")
    f = [(x * scale) % q for x in f]
    print("After scaling:", f)
    print()
    return f


def multiply_explained(f_hat, g_hat):
    print("=== Multiplying the two transformed lists together ===")
    print()
    h_hat = [0] * n
    for i in range(4):
        a0, a1 = f_hat[2 * i], f_hat[2 * i + 1]
        b0, b1 = g_hat[2 * i], g_hat[2 * i + 1]
        gamma = gammas[i]
        print(f"--- Pair {i+1}: f_hat gives ({a0},{a1}), g_hat gives ({b0},{b1}), magic number for this pair is {gamma} ---")

        c0 = (a0 * b0 + a1 * b1 * gamma) % q
        print(f"  First new number: ({a0}x{b0}) + ({a1}x{b1}x{gamma}) = {a0*b0} + {a1*b1*gamma} = {a0*b0 + a1*b1*gamma}, mod {q} is {c0}.")

        c1 = (a0 * b1 + a1 * b0) % q
        print(f"  Second new number: ({a0}x{b1}) + ({a1}x{b0}) = {a0*b1} + {a1*b0} = {a0*b1 + a1*b0}, mod {q} is {c1}.")
        print()

        h_hat[2 * i] = c0
        h_hat[2 * i + 1] = c1
    print("Combined result:", h_hat)
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


f = [1, 2, 0, 1, 0, 0, 1, 0]
g = [2, 0, 1, 0, 1, 0, 0, 1]

f_hat = NTT_explained(f, "f")
g_hat = NTT_explained(g, "g")
h_hat = multiply_explained(f_hat, g_hat)
result_ntt = NTT_inverse_explained(h_hat)

result_schoolbook = poly_mult_schoolbook(f, g)

print("=== Final check ===")
print("Schoolbook answer:", result_schoolbook)
print("NTT answer:       ", result_ntt)
print("Do they match?", result_schoolbook == result_ntt)
