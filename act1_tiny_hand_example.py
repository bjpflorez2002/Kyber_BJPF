import hashlib
import secrets

# real ML-KEM-1024 sizes now, reusing the already-verified building blocks
from Hashing_kyber_CBD_V2 import n, q, k, poly_add, poly_mult, CBD_TABLE, poly_builder

bytes_per_poly = 128  # eta=2 -> each byte gives 2 coefficients -> 128 bytes per polynomial


# ---- Step 1: rho ----
rho = secrets.token_bytes(32)
print("Step 1: rho =", rho.hex())
print()

# ---- Step 2: expand rho into the full k x k matrix A, one cell at a time ----
def make_poly_from_seed_real(seed):
    coefficients = []
    stream = hashlib.shake_128(seed).digest(700)  # generous supply
    for i in range(0, len(stream), 3):
        if len(coefficients) >= n:
            break
        b0, b1, b2 = stream[i], stream[i + 1], stream[i + 2]
        d1 = b0 + 256 * (b1 % 16)
        d2 = (b1 // 16) + 16 * b2
        if d1 < q:
            coefficients.append(d1)
        if d2 < q and len(coefficients) < n:
            coefficients.append(d2)

    if len(coefficients) < n:
        raise ValueError(
            f"ran out of bytes - only got {len(coefficients)} coefficients, needed {n}. "
            f"Need to request more bytes from the same stream and keep going."
        )

    return coefficients


A = []
for i in range(k):
    row = []
    for j in range(k):
        seed = rho + bytes([i, j])
        poly = make_poly_from_seed_real(seed)
        row.append(poly)
    A.append(row)

print("Step 2: A built -", k, "x", k, "matrix, each cell a", n, "-coefficient polynomial")
print("A[0][0] first 5 coefficients:", A[0][0][:5])
print()

# ---- Step 3 & 4: generate S and e using the real CBD_TABLE (eta=2) ----
def make_small_vector_real(seed):
    stream = hashlib.shake_256(seed).digest(k * bytes_per_poly)
    vector = []
    for i in range(k):
        poly_bytes = stream[i * bytes_per_poly: (i + 1) * bytes_per_poly]
        vector.append(poly_builder(poly_bytes, CBD_TABLE))
    return vector


s_seed = secrets.token_bytes(32)
e_seed = secrets.token_bytes(32)

S = make_small_vector_real(s_seed)
e = make_small_vector_real(e_seed)

print("Step 3: S built - S[0] first 5 coefficients:", S[0][:5])
print("Step 4: e built - e[0] first 5 coefficients:", e[0][:5])
print()

# ---- Step 5: b = A.S + e ----
b = []
for row_num in range(k):
    row = A[row_num]
    dot_product = [0] * n
    for i in range(k):
        dot_product = poly_add(dot_product, poly_mult(row[i], S[i]))
    b.append(poly_add(dot_product, e[row_num]))

print("Step 5: b built - b[0] first 5 coefficients:", b[0][:5])
print()

# ---- Step 6: Bob's public key ----
print("Step 6: Bob's public key = (rho, b) -", len(rho), "bytes of rho +", k, "polynomials of b")
print()

# ---- Step 7: H(ek) ----
combined = str(rho) + str(b)
H_ek = hashlib.sha3_256(combined.encode()).digest()
print("Step 7: H(ek) =", H_ek.hex())
print("(deterministic - same rho/b would always give this exact same value)")
print(seed)
print(seed)
