import random
import hashlib
import secrets

print("=== Setup: tools and lookup tables, nothing happens yet ===")
print()

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


# zeta - the 128 magic numbers straight from FIPS 203 Appendix A. not
# calculated, just given to us, same idea as CBD_TABLE was.
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

# zeta_reverse - zeta flipped end to end, so NTT_final walks forward
# through it instead of walking zeta backwards
zeta_reverse = list(reversed(zeta[1:128]))

# gamma - a SEPARATE table of 128 numbers, also from Appendix A, used only
# in c_hat_maker (the multiply step), one per pair
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


# hat_maker - turns a normal poly into its transformed shape. 7 rounds,
# pairing distance halves each round, every group grabs the next zeta in line
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


# NTT_final - undoes hat_maker. rounds go backwards, reads zeta_reverse
# forward, formula flips (add first then multiply), one last scaling step
# at the end cleans up a leftover factor from doing 7 rounds
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
    f = [(x * 3303) % q for x in f]
    return f


# c_hat_coefficient - handles just ONE pair during the multiply step
def c_hat_coefficient(a0, a1, b0, b1, gamma_value):
    c0 = (a0 * b0 + a1 * b1 * gamma_value) % q
    c1 = (a0 * b1 + a1 * b0) % q
    return c0, c1


# c_hat_maker - loops through all 128 pairs, builds the full c_hat list
def c_hat_maker(f_hat, g_hat):
    c_hat = [0] * n
    for i in range(128):
        c0, c1 = c_hat_coefficient(f_hat[2 * i], f_hat[2 * i + 1], g_hat[2 * i], g_hat[2 * i + 1], gamma[i])
        c_hat[2 * i] = c0
        c_hat[2 * i + 1] = c1
    return c_hat


# ntt_multiply - the NTT pipeline bundled into one drop-in replacement for
# poly_mult. same job, same answer, faster route.
def ntt_multiply(f, g):
    f_hat = hat_maker(f)
    g_hat = hat_maker(g)
    c_hat = c_hat_maker(f_hat, g_hat)
    return NTT_final(c_hat)


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


# bits_to_bytes and bytes_to_bits - just peel bits off one at a time (%2, //2)
# and pack them back the other way, same trick as bytes_to_bits from way back
# in the CBD work, just written as its own proper pair of functions now
def bits_to_bytes(bits):
    B = [0] * (len(bits) // 8)
    for i in range(len(bits)):
        B[i // 8] += bits[i] * (2 ** (i % 8))
    return bytes(B)


def bytes_to_bits(B):
    bits = []
    for byte_value in B:
        for _ in range(8):
            bits.append(byte_value % 2)
            byte_value //= 2
    return bits


# byte_encode - the real thing, replacing the str() shortcut. takes a list of
# n numbers (each fitting in d bits) and packs them straight into real bytes,
# no text, no wasted space, matches what a real ML-KEM implementation would produce
def byte_encode(F, d):
    bits = []
    for value in F:
        a = value
        for _ in range(d):
            bits.append(a % 2)
            a //= 2
    return bits_to_bytes(bits)


# byte_decode - undoes byte_encode, back into n real numbers
def byte_decode(B, d):
    bits = bytes_to_bits(B)
    modulus = q if d == 12 else (2 ** d)
    F = []
    for i in range(n):
        value = 0
        for j in range(d):
            value += bits[i * d + j] * (2 ** j)
        F.append(value % modulus)
    return F




















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


print("=== Setup done - all tools and tables ready ===")
print()
print("=== Act 1: Bob / KeyGen ===")

# rho - bobs random seed, 32 bytes. using secrets not random since this needs
# to be genuinely unguessable. this is the small thing bob actually shares -
# not the whole matrix A, anyone with rho can rebuild the exact same A from it later
rho = secrets.token_bytes(32)

print("rho =", rho)
print("length of rho in bytes =", len(rho))


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


# zed - bobs hidden backup value, 32 random bytes. never used unless a
# ciphertext check fails later in Act 3 - just sits here unused otherwise
zed = secrets.token_bytes(32)

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


# b = A.S + e, same as always (mod q, mod x^n+1) - using ntt_multiply
b = []
for row_num in range(k):
    row = A[row_num]
    dot_product = [0] * n
    for i in range(k):
        dot_product = poly_add(dot_product, ntt_multiply(row[i], S[i]))
    b.append(poly_add(dot_product, e[row_num]))

print()
print("b =", b)

print()
print("bobs public key is (rho, b) -", len(rho), "bytes of rho and", k, "polys for b")
print("s and e stay private, only bob sees these")


# H(ek) - hash bobs public key once, right now, and keep it. saves us
# from re-hashing (rho, b) from scratch every single time we need it later.
# using real byte_encode now instead of str() - proper packed bytes, not text
b_encoded = b"".join(byte_encode(poly, 12) for poly in b)
combined_bytes = rho + b_encoded
surprise_tool_to_help_us_later = hashlib.sha3_256(combined_bytes).digest()

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
# same hash bob already computed and stored, she's just redoing it on her side.
# real byte_encode again, not str()
Alice_b_encoded = b"".join(byte_encode(poly, 12) for poly in b)
Alice_combined_bytes = rho + Alice_b_encoded
Alice_HEK = hashlib.sha3_256(Alice_combined_bytes).digest()

print("does alice_hek match what bob already has:", Alice_HEK == surprise_tool_to_help_us_later)


# m - alices actual message, n random bits, one per coefficient. using
# secrets not random since literally everything else gets derived from this
m = []
for i in range(n):
    m.append(secrets.choice([0, 1]))


# hash (m + Alice_HEK) using sha3_512, get 64 bytes back, split down the middle:
# first half = K, the actual shared secret, put this aside for later
# second half = the seed that r, e_one and e_two get generated from.
# m is a list of bits, so byte_encode with d=1 just packs 8 bits per byte
m_encoded_bytes = byte_encode(m, 1)
combined_m_hek_bytes = m_encoded_bytes + Alice_HEK
g_output = hashlib.sha3_512(combined_m_hek_bytes).digest()
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

# u = A_t x r + e_one - using ntt_multiply
u = []
for row_num in range(k):
    row = A_t[row_num]
    dot_product = [0] * n
    for i in range(k):
        dot_product = poly_add(dot_product, ntt_multiply(row[i], r[i]))
    u.append(poly_add(dot_product, e_one[row_num]))

# v = b_t . r + e_two + m_encoded - using ntt_multiply
dot_product = [0] * n
for i in range(k):
    dot_product = poly_add(dot_product, ntt_multiply(b_t[i], r[i]))
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
    dot_product = poly_add(dot_product, ntt_multiply(S_t[i], u[i]))
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
# stored H(ek) (surprise_tool_to_help_us_later) instead of recomputing it.
# real byte_encode for m_recovered too, same as alice did for m
m_recovered_bytes = byte_encode(m_recovered, 1)
combined_m_hek_bob_bytes = m_recovered_bytes + surprise_tool_to_help_us_later
g_output_bob = hashlib.sha3_512(combined_m_hek_bob_bytes).digest()
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
# bobs own A this time (not Alice_A, he already had the real one) and b -
# using ntt_multiply
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
        dot_product = poly_add(dot_product, ntt_multiply(row[i], r_prime[i]))
    u_prime.append(poly_add(dot_product, e_one_prime[row_num]))

dot_product = [0] * n
for i in range(k):
    dot_product = poly_add(dot_product, ntt_multiply(b_t_bob[i], r_prime[i]))
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
    # imposter_protocol - glue zed and the ciphertext together and hash them.
    # this becomes K_final instead, so a rejected message still produces a
    # normal-looking 32-byte key, same as the real path would.
    # u is k separate polys so each one needs encoding then joining together,
    # v is just one poly so it encodes directly
    u_encoded = b"".join(byte_encode(poly, 12) for poly in u)
    v_encoded = byte_encode(v, 12)
    imposter_protocol = zed + u_encoded + v_encoded
    K_final = hashlib.shake_256(imposter_protocol).digest(32)
    print("ciphertext check failed, using zed to build a fallback K_final instead")

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
    