# Bob, key generation, establishing A, S and e, calculating b and then sharing A and b

import random

q = 97  # the modulus we work in

# A: 3x3 matrix, each cell a random number between 0 and q-1
A = []
for row_num in range(3):
    row = []
    for col_num in range(3):
        row.append(random.randint(0, q - 1))
    A.append(row)

# S: 3x1 vector (Bob's secret), each cell a random number between 0 and q-1
S = []
for i in range(3):
    S.append(random.choice([-1,0,1]))

# e: 3x1 vector (small error), each cell randomly -1, 0, or 1
e = []
for i in range(3):
    e.append(random.choice([-1, 0, 1]))

# b = A x S + e (mod q)
b = []
for row_num in range(3):
    row = A[row_num]
    dot_product = 0
    for i in range(3):
        dot_product += row[i] * S[i]
    b.append((dot_product + e[row_num]) % q)

print("q =", q)
print("A =", A)
print("S =", S)
print("e =", e)
print("b =", b)
print()
print("Bob shares (A, b) publicly. S stays private.")














# Alice receives A and b and creates u and v with her new values of e_one,
# e_two, r and, most importantly, her message m which she encodes and sends
# u and v

# r: 3x1 vector, each cell randomly -1, 0, or 1
r = []
for i in range(3):
    r.append(random.choice([-1, 0, 1]))

# e_one: 3x1 vector (small error), each cell randomly -1, 0, or 1
e_one = []
for i in range(3):
    e_one.append(random.choice([-1, 0, 1]))

# e_two: a single small error, randomly -1, 0, or 1
e_two = random.choice([-1, 0, 1])

# m: Alice's secret message bit, randomly 0 or 1
m = random.choice([0, 1])

# m_encoded: turn the bit into 0 or q//2
m_encoded = (q // 2) * m

# A_t: transpose of A (swap rows and columns)
A_t = []
for col_num in range(3):
    new_row = []
    for row_num in range(3):
        new_row.append(A[row_num][col_num])
    A_t.append(new_row)

# b_t: just b, no computation needed (a vector's transpose doesn't move anything)
b_t = b

# u = A_t x r + e_one (mod q)
u = []
for row_num in range(3):
    row = A_t[row_num]
    dot_product = 0
    for i in range(3):
        dot_product += row[i] * r[i]
    u.append((dot_product + e_one[row_num]) % q)

# v = b_t . r + e_two + m_encoded (mod q)
dot_product = 0
for i in range(3):
    dot_product += b_t[i] * r[i]
v = (dot_product + e_two + m_encoded) % q

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

# w = v - S_t . u (mod q)
dot_product = 0
for i in range(3):
    dot_product += S_t[i] * u[i]
w = (v - dot_product) % q

print()
print("w =", w)

# check if w is closer to 0 or closer to q//2, to recover Alice's message m
# (going the short way around the clock, not just a straight line subtraction)
zero_check = min(abs(w - 0), abs(w - q))
half_check = abs(w - q // 2)

if half_check > zero_check:
    m_recovered = 0
else:
    m_recovered = 1

print("m_recovered =", m_recovered)
print("m was actually =", m)
print("match:", m_recovered == m)
