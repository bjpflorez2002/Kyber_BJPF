import random
import hashlib
import secrets

# n - how many coefficients each polynomial has, so the highest degree
#     possible is n-1
# q - the modulus were working in
# k - the matrix/vector size, so its a k x k matrix and k-long vectors

n = 256  # degree of each polynomial
q = 3329  # the modulus we work in
k = 4  # matrix/vector size


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
    # stage 1 - just multiply everything out normally, this can reach degree 2n-2
    zeroed_poly = [0] * (2 * n - 1)
    for i in range(n):
        for j in range(n):
            zeroed_poly[i + j] = (zeroed_poly[i + j] + f[i] * g[j]) % q

    # zeroed_poly is fully filled now, rename it to match what it actually is
    full_poly_product = zeroed_poly

    # stage 2 - fold anything sitting at position n or higher back down, using x^n = -1
    folded = [0] * n
    for i in range(n):
        folded[i] = full_poly_product[i]
    for i in range(n, 2 * n - 1):
        wrapped_position = i - n
        folded[wrapped_position] = (folded[wrapped_position] - full_poly_product[i]) % q

    return folded


# CBD_TABLE - every possible byte value (0-255), written out by hand,
# mapped to the 2 coefficients it gives when eta=2
CBD_TABLE = {
    0: [0, 0],
    1: [1, 0],
    2: [1, 0],
    3: [2, 0],
    4: [-1, 0],
    5: [0, 0],
    6: [0, 0],
    7: [1, 0],
    8: [-1, 0],
    9: [0, 0],
    10: [0, 0],
    11: [1, 0],
    12: [-2, 0],
    13: [-1, 0],
    14: [-1, 0],
    15: [0, 0],
    16: [0, 1],
    17: [1, 1],
    18: [1, 1],
    19: [2, 1],
    20: [-1, 1],
    21: [0, 1],
    22: [0, 1],
    23: [1, 1],
    24: [-1, 1],
    25: [0, 1],
    26: [0, 1],
    27: [1, 1],
    28: [-2, 1],
    29: [-1, 1],
    30: [-1, 1],
    31: [0, 1],
    32: [0, 1],
    33: [1, 1],
    34: [1, 1],
    35: [2, 1],
    36: [-1, 1],
    37: [0, 1],
    38: [0, 1],
    39: [1, 1],
    40: [-1, 1],
    41: [0, 1],
    42: [0, 1],
    43: [1, 1],
    44: [-2, 1],
    45: [-1, 1],
    46: [-1, 1],
    47: [0, 1],
    48: [0, 2],
    49: [1, 2],
    50: [1, 2],
    51: [2, 2],
    52: [-1, 2],
    53: [0, 2],
    54: [0, 2],
    55: [1, 2],
    56: [-1, 2],
    57: [0, 2],
    58: [0, 2],
    59: [1, 2],
    60: [-2, 2],
    61: [-1, 2],
    62: [-1, 2],
    63: [0, 2],
    64: [0, -1],
    65: [1, -1],
    66: [1, -1],
    67: [2, -1],
    68: [-1, -1],
    69: [0, -1],
    70: [0, -1],
    71: [1, -1],
    72: [-1, -1],
    73: [0, -1],
    74: [0, -1],
    75: [1, -1],
    76: [-2, -1],
    77: [-1, -1],
    78: [-1, -1],
    79: [0, -1],
    80: [0, 0],
    81: [1, 0],
    82: [1, 0],
    83: [2, 0],
    84: [-1, 0],
    85: [0, 0],
    86: [0, 0],
    87: [1, 0],
    88: [-1, 0],
    89: [0, 0],
    90: [0, 0],
    91: [1, 0],
    92: [-2, 0],
    93: [-1, 0],
    94: [-1, 0],
    95: [0, 0],
    96: [0, 0],
    97: [1, 0],
    98: [1, 0],
    99: [2, 0],
    100: [-1, 0],
    101: [0, 0],
    102: [0, 0],
    103: [1, 0],
    104: [-1, 0],
    105: [0, 0],
    106: [0, 0],
    107: [1, 0],
    108: [-2, 0],
    109: [-1, 0],
    110: [-1, 0],
    111: [0, 0],
    112: [0, 1],
    113: [1, 1],
    114: [1, 1],
    115: [2, 1],
    116: [-1, 1],
    117: [0, 1],
    118: [0, 1],
    119: [1, 1],
    120: [-1, 1],
    121: [0, 1],
    122: [0, 1],
    123: [1, 1],
    124: [-2, 1],
    125: [-1, 1],
    126: [-1, 1],
    127: [0, 1],
    128: [0, -1],
    129: [1, -1],
    130: [1, -1],
    131: [2, -1],
    132: [-1, -1],
    133: [0, -1],
    134: [0, -1],
    135: [1, -1],
    136: [-1, -1],
    137: [0, -1],
    138: [0, -1],
    139: [1, -1],
    140: [-2, -1],
    141: [-1, -1],
    142: [-1, -1],
    143: [0, -1],
    144: [0, 0],
    145: [1, 0],
    146: [1, 0],
    147: [2, 0],
    148: [-1, 0],
    149: [0, 0],
    150: [0, 0],
    151: [1, 0],
    152: [-1, 0],
    153: [0, 0],
    154: [0, 0],
    155: [1, 0],
    156: [-2, 0],
    157: [-1, 0],
    158: [-1, 0],
    159: [0, 0],
    160: [0, 0],
    161: [1, 0],
    162: [1, 0],
    163: [2, 0],
    164: [-1, 0],
    165: [0, 0],
    166: [0, 0],
    167: [1, 0],
    168: [-1, 0],
    169: [0, 0],
    170: [0, 0],
    171: [1, 0],
    172: [-2, 0],
    173: [-1, 0],
    174: [-1, 0],
    175: [0, 0],
    176: [0, 1],
    177: [1, 1],
    178: [1, 1],
    179: [2, 1],
    180: [-1, 1],
    181: [0, 1],
    182: [0, 1],
    183: [1, 1],
    184: [-1, 1],
    185: [0, 1],
    186: [0, 1],
    187: [1, 1],
    188: [-2, 1],
    189: [-1, 1],
    190: [-1, 1],
    191: [0, 1],
    192: [0, -2],
    193: [1, -2],
    194: [1, -2],
    195: [2, -2],
    196: [-1, -2],
    197: [0, -2],
    198: [0, -2],
    199: [1, -2],
    200: [-1, -2],
    201: [0, -2],
    202: [0, -2],
    203: [1, -2],
    204: [-2, -2],
    205: [-1, -2],
    206: [-1, -2],
    207: [0, -2],
    208: [0, -1],
    209: [1, -1],
    210: [1, -1],
    211: [2, -1],
    212: [-1, -1],
    213: [0, -1],
    214: [0, -1],
    215: [1, -1],
    216: [-1, -1],
    217: [0, -1],
    218: [0, -1],
    219: [1, -1],
    220: [-2, -1],
    221: [-1, -1],
    222: [-1, -1],
    223: [0, -1],
    224: [0, -1],
    225: [1, -1],
    226: [1, -1],
    227: [2, -1],
    228: [-1, -1],
    229: [0, -1],
    230: [0, -1],
    231: [1, -1],
    232: [-1, -1],
    233: [0, -1],
    234: [0, -1],
    235: [1, -1],
    236: [-2, -1],
    237: [-1, -1],
    238: [-1, -1],
    239: [0, -1],
    240: [0, 0],
    241: [1, 0],
    242: [1, 0],
    243: [2, 0],
    244: [-1, 0],
    245: [0, 0],
    246: [0, 0],
    247: [1, 0],
    248: [-1, 0],
    249: [0, 0],
    250: [0, 0],
    251: [1, 0],
    252: [-2, 0],
    253: [-1, 0],
    254: [-1, 0],
    255: [0, 0],
}


def poly_builder(poly_bytes, table):
    coefficients = []
    for byte_value in poly_bytes:
        coefficients.extend(table[byte_value])
    return coefficients


# rho - bobs random seed, 32 bytes. using secrets not random since this needs
# to be genuinely unguessable. this is the small thing bob actually shares -
# not the whole matrix A, anyone with rho can rebuild A themselves later
rho = secrets.token_bytes(32)

print("rho =", rho)
print("length of rho in bytes =", len(rho))


# poly_generator_from_seed - give it a seed already tagged for one cell,
# it stretches that with shake_128 and reads the stream 3 bytes at a time.
# each group of 3 bytes gives 2 candidate numbers (d1, d2). keep whatever
# is under q, throw away anything too big, stop once we have 256 coefficients
def poly_generator_from_seed(seed):
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
        raise ValueError(f"ran out of bytes - only got {len(coefficients)} coefficients, needed {n}")

    return coefficients


# A - the k x k matrix. built by tagging rho with each cells row/col
# and running it through poly_generator_from_seed, not random.randint
A = []
for row_num in range(k):
    row = []
    for col_num in range(k):
        cell_seed = rho + bytes([row_num, col_num])
        poly = poly_generator_from_seed(cell_seed)
        row.append(poly)
    A.append(row)

print()
print("A =", A)


# S and e - one shared seed (sigma), just tagged with a different position
# byte for each polynomial. S gets positions 0..k-1, then e just keeps
# counting on from there (k..2k-1) instead of using a second seed
sigma = secrets.token_bytes(32)

S = []
for position in range(k):
    cell_seed = sigma + bytes([position])
    stream = hashlib.shake_256(cell_seed).digest(128)  # eta=2 -> 128 bytes -> 256 coefficients
    S.append(poly_builder(stream, CBD_TABLE))

e = []
for position in range(k, 2 * k):
    cell_seed = sigma + bytes([position])
    stream = hashlib.shake_256(cell_seed).digest(128)
    e.append(poly_builder(stream, CBD_TABLE))

print()
print("S =", S)
print("e =", e)


# b = A.S + e, same as always (mod q, mod x^n+1)
b = []
for row_num in range(k):
    row = A[row_num]
    dot_product = [0] * n
    for i in range(k):
        dot_product = poly_add(dot_product, poly_mult(row[i], S[i]))
    b.append(poly_add(dot_product, e[row_num]))

print()
print("b =", b)

print()
print("bobs public key is (rho, b) -", len(rho), "bytes of rho and", k, "polys for b")
print("s and e stay private, only bob sees these")


# H(ek) - hash bobs public key once, right now, and keep it. saves us
# from re-hashing (rho, b) from scratch every single time we need it later
combined = str(rho) + str(b)
surprise_tool_to_help_us_later = hashlib.sha3_256(combined.encode()).digest()

print()
print("surprise_tool_to_help_us_later, aka H(ek) =", surprise_tool_to_help_us_later.hex())





































print()
print("=== Act 2: Alice / Encapsulate ===")

# Alice_A - alice rebuilds A herself from rho. she never actually gets the
# matrix sent to her, just (rho, b) - same expansion bob used to build his A
Alice_A = []
for row_num in range(k):
    row = []
    for col_num in range(k):
        cell_seed = rho + bytes([row_num, col_num])
        poly = poly_generator_from_seed(cell_seed)
        row.append(poly)
    Alice_A.append(row)

print()
print("alice rebuilt A herself, does it match bobs A:", Alice_A == A)


# Alice_HEK - alice works out H(ek) herself from the (rho, b) she got.
# same hash bob already computed and stored, she's just redoing it on her side
Alice_combined = str(rho) + str(b)
Alice_HEK = hashlib.sha3_256(Alice_combined.encode()).digest()

print("does alice_hek match what bob already has:", Alice_HEK == surprise_tool_to_help_us_later)


# m - alices actual message, n random bits, one per coefficient. using
# secrets not random since literally everything else gets derived from this
m = []
for i in range(n):
    m.append(secrets.choice([0, 1]))


# hash (m + Alice_HEK) using sha3_512, get 64 bytes back, split down the middle:
# first half = K, the actual shared secret, put this aside for later
# second half = the seed that r, e_one and e_two get generated from
combined_m_hek = str(m) + str(Alice_HEK)
g_output = hashlib.sha3_512(combined_m_hek.encode()).digest()
K = g_output[0:32]
r_coins = g_output[32:64]

print()
print("K, the real shared secret, saving this for later =", K.hex())


# r, e_one, e_two - same one-seed-plus-position trick we used for S/e.
# r takes positions 0..k-1, e_one carries on with k..2k-1, e_two gets position 2k
r = []
for position in range(k):
    cell_seed = r_coins + bytes([position])
    stream = hashlib.shake_256(cell_seed).digest(128)
    r.append(poly_builder(stream, CBD_TABLE))

e_one = []
for position in range(k, 2 * k):
    cell_seed = r_coins + bytes([position])
    stream = hashlib.shake_256(cell_seed).digest(128)
    e_one.append(poly_builder(stream, CBD_TABLE))

cell_seed = r_coins + bytes([2 * k])
stream = hashlib.shake_256(cell_seed).digest(128)
e_two = poly_builder(stream, CBD_TABLE)

print()
print("r =", r)
print("e_one =", e_one)
print("e_two =", e_two)


# m_encoded - turn every bit of m into either 0 or q//2
m_encoded = []
for i in range(n):
    m_encoded.append((q // 2) * m[i])


# A_t - just the transpose of Alice_A
A_t = []
for col_num in range(k):
    new_row = []
    for row_num in range(k):
        new_row.append(Alice_A[row_num][col_num])
    A_t.append(new_row)

# b_t - literally just b, a vector transpose is a no-op
b_t = b

# u = A_t x r + e_one
u = []
for row_num in range(k):
    row = A_t[row_num]
    dot_product = [0] * n
    for i in range(k):
        dot_product = poly_add(dot_product, poly_mult(row[i], r[i]))
    u.append(poly_add(dot_product, e_one[row_num]))

# v = b_t . r + e_two + m_encoded
dot_product = [0] * n
for i in range(k):
    dot_product = poly_add(dot_product, poly_mult(b_t[i], r[i]))
v = poly_add(poly_add(dot_product, e_two), m_encoded)

print()
print("u =", u)
print("v =", v)
print()
print("alice sends u and v over to bob")





































print()
print("=== Act 3: Bob / Decapsulate ===")

# step 1 - bob works out m_recovered from (u, v) using his private S.
# nothing new here, same algebra as the very first toy build
S_t = S

dot_product = [0] * n
for i in range(k):
    dot_product = poly_add(dot_product, poly_mult(S_t[i], u[i]))
w = poly_sub(v, dot_product)

m_recovered = []
for i in range(n):
    zero_check = min(abs(w[i] - 0), abs(w[i] - q))
    half_check = abs(w[i] - q // 2)
    if half_check > zero_check:
        m_recovered.append(0)
    else:
        m_recovered.append(1)

print()
print("does m_recovered match alices m:", m_recovered == m)


# step 2 - bob re-hashes (m_recovered + H(ek)), but reuses his already-
# stored H(ek) (surprise_tool_to_help_us_later) instead of recomputing it
combined_m_hek_bob = str(m_recovered) + str(surprise_tool_to_help_us_later)
g_output_bob = hashlib.sha3_512(combined_m_hek_bob.encode()).digest()
K_prime = g_output_bob[0:32]
r_coins_prime = g_output_bob[32:64]


# step 3 - regenerate r', e_one', e_two' from r_coins', same position-tagged
# shake_256 + CBD table trick as before, nothing new
r_prime = []
for position in range(k):
    cell_seed = r_coins_prime + bytes([position])
    stream = hashlib.shake_256(cell_seed).digest(128)
    r_prime.append(poly_builder(stream, CBD_TABLE))

e_one_prime = []
for position in range(k, 2 * k):
    cell_seed = r_coins_prime + bytes([position])
    stream = hashlib.shake_256(cell_seed).digest(128)
    e_one_prime.append(poly_builder(stream, CBD_TABLE))

cell_seed = r_coins_prime + bytes([2 * k])
stream = hashlib.shake_256(cell_seed).digest(128)
e_two_prime = poly_builder(stream, CBD_TABLE)


# step 4 - recompute u', v' with the same formulas alice used, just using
# bobs own A this time (not Alice_A, he already had the real one) and b
m_recovered_encoded = []
for i in range(n):
    m_recovered_encoded.append((q // 2) * m_recovered[i])

A_t_bob = []
for col_num in range(k):
    new_row = []
    for row_num in range(k):
        new_row.append(A[row_num][col_num])
    A_t_bob.append(new_row)

b_t_bob = b

u_prime = []
for row_num in range(k):
    row = A_t_bob[row_num]
    dot_product = [0] * n
    for i in range(k):
        dot_product = poly_add(dot_product, poly_mult(row[i], r_prime[i]))
    u_prime.append(poly_add(dot_product, e_one_prime[row_num]))

dot_product = [0] * n
for i in range(k):
    dot_product = poly_add(dot_product, poly_mult(b_t_bob[i], r_prime[i]))
v_prime = poly_add(poly_add(dot_product, e_two_prime), m_recovered_encoded)


# step 5 and 6 - check (u', v') against the real (u, v) alice sent.
# if they match, K' is confirmed as the real shared secret
ciphertext_matches = (u_prime == u) and (v_prime == v)

print("does u_prime match the real u:", u_prime == u)
print("does v_prime match the real v:", v_prime == v)
print()

if ciphertext_matches:
    K_final = K_prime
    print("ciphertext check passed, K_prime is now the confirmed shared secret")
else:
    print("ciphertext check failed, havent built the fallback yet")
    K_final = None

print()
print("K_final =", K_final.hex() if K_final else None)
print("does this match alices K:", K_final == K if K_final else False)


































print()
print("=== Act 4: starting the AES-256 key matrix ===")

# K_final is 32 bytes. AES-256 lays its starting key out as 4 rows by 8
# columns (4*8=32), filling down each column first before moving to the next -
# thats just AES's standard fill order
aes_key_matrix = [[0] * 8 for _ in range(4)]

for byte_index in range(32):
    row = byte_index % 4
    col = byte_index // 4
    aes_key_matrix[row][col] = K_final[byte_index]

print()
print("aes-256 starting key matrix, 4 rows by 8 columns:")
for row in aes_key_matrix:
    print(["%02x" % b for b in row])
