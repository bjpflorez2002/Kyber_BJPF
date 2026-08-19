n = 256
q = 3329


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


# byte_encode - packs a list of n integers (each fitting in d bits) into real bytes
def byte_encode(F, d):
    bits = []
    for value in F:
        a = value
        for _ in range(d):
            bits.append(a % 2)
            a //= 2
    return bits_to_bytes(bits)


# byte_decode - the reverse, unpacks bytes back into n integers
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


# quick test: a real 256-coefficient polynomial, round-trip through encode/decode
import random
random.seed(1)
poly = [random.randint(0, q - 1) for _ in range(n)]

encoded = byte_encode(poly, 12)
decoded = byte_decode(encoded, 12)

print("original poly (first 5):", poly[:5])
print("encoded length in bytes:", len(encoded), "(expected 384 = 256*12/8)")
print("decoded poly (first 5): ", decoded[:5])
print("ROUND TRIP MATCH:", poly == decoded)
