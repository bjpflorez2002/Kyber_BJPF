import random

n = 256
q = 3329


# compress_u / decompress_u - always uses du=11, nothing to pass in
def compress_u(x):
    numerator = 2048 * x  # 2^11
    rounded = (numerator + q // 2) // q
    return rounded % 2048


def decompress_u(y):
    numerator = q * y
    rounded = (numerator + 1024) // 2048  # 2^(11-1)
    return rounded


# compress_v / decompress_v - always uses dv=5, nothing to pass in
def compress_v(x):
    numerator = 32 * x  # 2^5
    rounded = (numerator + q // 2) // q
    return rounded % 32


def decompress_v(y):
    numerator = q * y
    rounded = (numerator + 16) // 32  # 2^(5-1)
    return rounded


def compress_u_poly(poly):
    return [compress_u(x) for x in poly]


def decompress_u_poly(poly):
    return [decompress_u(y) for y in poly]


def compress_v_poly(poly):
    return [compress_v(x) for x in poly]


def decompress_v_poly(poly):
    return [decompress_v(y) for y in poly]


# --- test: real-scale polynomial through each pair ---
random.seed(7)
poly = [random.randint(0, q - 1) for _ in range(n)]

u_compressed = compress_u_poly(poly)
u_decompressed = decompress_u_poly(u_compressed)
u_max_error = max(abs(a - b) for a, b in zip(poly, u_decompressed))

v_compressed = compress_v_poly(poly)
v_decompressed = decompress_v_poly(v_compressed)
v_max_error = max(abs(a - b) for a, b in zip(poly, v_decompressed))

print("=== compress_u / decompress_u (du=11) ===")
print("original (first 5):     ", poly[:5])
print("compressed (first 5):   ", u_compressed[:5])
print("decompressed (first 5): ", u_decompressed[:5])
print("biggest difference:", u_max_error)

print()
print("=== compress_v / decompress_v (dv=5) ===")
print("original (first 5):     ", poly[:5])
print("compressed (first 5):   ", v_compressed[:5])
print("decompressed (first 5): ", v_decompressed[:5])
print("biggest difference:", v_max_error)
