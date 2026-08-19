# Bob, key generation, establishing A, S and e, calculating b and then sharing A and b
# Polynomial version: same shape as toy_integer_kyber_3x3.py, but each "number"
# is now a polynomial - a list of n coefficients - using poly_add and poly_mult
# instead of plain + and *

import random

# n = size of each polynomial - it has n coefficients, so the highest
#     possible degree is n-1 (the ring size)
# q = the modulus
# k = the matrix/vector size - a k x k matrix, k-long vectors

n = 256  # degree of each polynomial (4 coefficients)
q = 3329  # the modulus we work in
k = 4  # matrix/vector size (3x3, matching the integer version)


def poly_add(f, g):
    added = []
    for i in range(n):
        added.append((f[i] + g[i]) % q)
    return added


def poly_sub(f, g):
    subtracted = []
    for i in range(n):
        subtracted.append((f[i] - g[i]) % q)
    return subtracted


def poly_mult(f, g):
    # stage 1: multiply everything out normally - can go up to degree 2n-2 (7 slots here)
    zeroed_poly = [0] * (2 * n - 1)
    for i in range(n):
        for j in range(n):
            zeroed_poly[i + j] = (zeroed_poly[i + j] + f[i] * g[j]) % q

    # zeroed_poly is now fully filled in - give it a name matching what it now is
    full_poly_product = zeroed_poly

    # stage 2: fold anything at position n or higher back down, using x^n = -1
    folded = [0] * n
    for i in range(n):
        folded[i] = full_poly_product[i]
    for i in range(n, 2 * n - 1):
        wrapped_position = i - n
        folded[wrapped_position] = (folded[wrapped_position] - full_poly_product[i]) % q

    return folded


# A: k x k matrix, each cell a polynomial with n random coefficients between 0 and q-1
A = []
for row_num in range(k):
    row = []
    for col_num in range(k):
        poly = []
        for i in range(n):
            poly.append(random.randint(0, q - 1))
        row.append(poly)
    A.append(row)

# S: k x 1 vector of polynomials (Bob's secret), each coefficient randomly -1, 0, or 1
S = []
for i in range(k):
    poly = []
    for j in range(n):
        poly.append(random.choice([-1, 0, 1]))
    S.append(poly)

# e: k x 1 vector of polynomials (small error), same shape as S
e = []
for i in range(k):
    poly = []
    for j in range(n):
        poly.append(random.choice([-1, 0, 1]))
    e.append(poly)

# b = A x S + e (mod q, mod x^n+1)
b = []
for row_num in range(k):
    row = A[row_num]
    dot_product = [0] * n
    for i in range(k):
        dot_product = poly_add(dot_product, poly_mult(row[i], S[i]))
    b.append(poly_add(dot_product, e[row_num]))

print("A =", A)
print("S =", S)
print("e =", e)
print("b =", b)
print()
print("Bob shares (A, b) publicly. S stays private.")

















# Alice receives A and b and creates u and v with her new values of e_one,
# e_two, r and, most importantly, her message m which she encodes and sends
# u and v

# r: k x 1 vector of polynomials, each coefficient randomly -1, 0, or 1
r = []
for i in range(k):
    poly = []
    for j in range(n):
        poly.append(random.choice([-1, 0, 1]))
    r.append(poly)

# e_one: k x 1 vector of polynomials (small error), same shape as r
e_one = []
for i in range(k):
    poly = []
    for j in range(n):
        poly.append(random.choice([-1, 0, 1]))
    e_one.append(poly)

# e_two: a single small polynomial, coefficients randomly -1, 0, or 1
poly = []
for i in range(n):
    poly.append(random.choice([-1, 0, 1]))
e_two = poly

# m: n random bits, Alice's secret message, one bit per coefficient
m = []
for i in range(n):
    m.append(random.choice([0, 1]))

# m_encoded: turn each bit into 0 or q//2
m_encoded = []
for i in range(n):
    m_encoded.append((q // 2) * m[i])

# A_t: transpose of A - swap rows and columns, moving whole polynomials
A_t = []
for col_num in range(k):
    new_row = []
    for row_num in range(k):
        new_row.append(A[row_num][col_num])
    A_t.append(new_row)

# b_t: just b, no computation needed (a vector's transpose doesn't move anything)
b_t = b

# u = A_t x r + e_one (mod q, mod x^n+1)
u = []
for row_num in range(k):
    row = A_t[row_num]
    dot_product = [0] * n
    for i in range(k):
        dot_product = poly_add(dot_product, poly_mult(row[i], r[i]))
    u.append(poly_add(dot_product, e_one[row_num]))

# v = b_t . r + e_two + m_encoded (mod q, mod x^n+1)
dot_product = [0] * n
for i in range(k):
    dot_product = poly_add(dot_product, poly_mult(b_t[i], r[i]))
v = poly_add(poly_add(dot_product, e_two), m_encoded)

print()
print("r =", r)
print("e_one =", e_one)
print("e_two =", e_two)
print("m =", m)
print("m_encoded =", m_encoded)
print("A_t =", A_t)
print("u =", u)
print("v =", v)
print()
print("Alice sends (u, v) to Bob.")

















# Bob receives (u, v) and uses his private S to calculate w, which he will
# round to recover Alice's message m

# S_t: just S, no computation needed (a vector's transpose doesn't move anything)
S_t = S

# w = v - S_t . u (mod q, mod x^n+1)
dot_product = [0] * n
for i in range(k):
    dot_product = poly_add(dot_product, poly_mult(S_t[i], u[i]))
w = poly_sub(v, dot_product)

# check each coefficient of w against 0 and q//2, to recover Alice's message m
m_recovered = []
for i in range(n):
    zero_check = min(abs(w[i] - 0), abs(w[i] - q))
    half_check = abs(w[i] - q // 2)

    if half_check > zero_check:
        m_recovered.append(0)
    else:
        m_recovered.append(1)

print()
print("w =", w)
print("m_recovered =", m_recovered)
print("m was actually =", m)
print("match:", m_recovered == m)
