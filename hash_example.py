import hashlib

# small example values - change these and re-run to see the hash change completely
m = [1, 1]
A = [[4, 4], [20, 4]]
b = [5, 1]

print(A)

# step 1: glue everything together into one string
combined = str(m) + str(A) + str(b)
print("combined string =", repr(combined))

# step 2: we are changing from a string to bytes so then the hashing
# function can work - hash functions only accept bytes, not plain text
# .encode() converts each character into its number using UTF-8, which for
# normal characters (digits, brackets, commas, spaces) is the same as ASCII -
# e.g. '[' -> 91, '1' -> 49, ',' -> 44, ' ' -> 32, '0' -> 48, ']' -> 93
combined_bytes = combined.encode()
print("combined bytes  =", combined_bytes)

# step 3: hash it - same input always gives the same output,
# but a tiny change to the input gives a completely different output
hash_output = hashlib.sha3_512(combined_bytes).digest()
print("hash output (raw bytes) =", hash_output)

# step 4: hash_output is only 64 bytes, but we need way more than that
# (1152 bytes, to eventually cover r, e_one, e_two) - sha3_512 can't give us
# more than 64 bytes no matter what, so we feed hash_output into shake_256
# instead, which lets us ask for exactly how many bytes we want
seed = hash_output
big_output = hashlib.shake_256(seed).digest(1152)
print()
print("seed (same as hash_output) =", seed)
print("big output length =", len(big_output))
print("big output =", big_output)

# step 5: use the pre-built CBD_TABLE to turn big_output into r, e_one, e_two
# CBD_TABLE: every possible byte (0-255), written out explicitly,
# mapped to the 2 coefficients it produces when eta=2.
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

n = 256    # coefficients per polynomial
k = 4      # how many polynomials in r and in e_one
bytes_per_poly = 128  # eta=2 -> each byte gives 2 coefficients -> 128 bytes per polynomial

r_bytes = big_output[0:512]
e_one_bytes = big_output[512:1024]
e_two_bytes = big_output[1024:1152]


def poly_builder(poly_bytes, table):
    coefficients = []
    for byte_value in poly_bytes:
        coefficients.extend(table[byte_value])
    return coefficients


# gets the first quarter of bytes then adds it, then the same with the
# other quarters (4 quarters total, since k=4)
r = []
for i in range(k):
    poly_bytes = r_bytes[i * bytes_per_poly: (i + 1) * bytes_per_poly]
    poly = poly_builder(poly_bytes, CBD_TABLE)
    r.append(poly)

e_one = []
for i in range(k):
    poly_bytes = e_one_bytes[i * bytes_per_poly: (i + 1) * bytes_per_poly]
    poly = poly_builder(poly_bytes, CBD_TABLE)
    e_one.append(poly)

e_two = poly_builder(e_two_bytes, CBD_TABLE)

print()
print("r[0] (first polynomial only) =", r[0])
print("e_one[0] (first polynomial only) =", e_one[0])
print("e_two =", e_two)