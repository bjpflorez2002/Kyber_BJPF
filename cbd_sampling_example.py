# BytesToBits: turn each byte into its 8 individual bits (0s and 1s)
# has a list, for each byte in B (outer loop, once per byte): the value is
# the byte, then for 8 passes (inner loop, once per bit): it adds the value
# of 1 or 0 by checking mod 2, then it makes a new value of the current
# value // 2
def bytes_to_bits(B):
    bits = []
    for byte in B:
        value = byte
        for j in range(8):
            bits.append(value % 2)
            value = value // 2
    return bits


# SamplePolyCBD: use eta bits, then the next eta bits, to build one small
# coefficient at a time (x - y trick)
def sample_poly_cbd(bits, eta, num_coefficients, verbose=True):
    coefficients = []
    for i in range(num_coefficients):
        x_bits = bits[2 * i * eta: 2 * i * eta + eta]
        y_bits = bits[2 * i * eta + eta: 2 * i * eta + 2 * eta]
        x = sum(x_bits)
        y = sum(y_bits)
        coefficient = x - y
        if verbose:
            print(f"coefficient {i}: x_bits={x_bits} (x={x}), y_bits={y_bits} (y={y}), coefficient = {x} - {y} = {coefficient}")
        coefficients.append(coefficient)
    return coefficients


# build_cbd_table: precompute the 2 coefficients every possible byte (0-255)
# would produce, only works because eta=2 means each byte's 8 bits divide
# evenly into exactly 2 self-contained coefficients (4 bits each)
def build_cbd_table(eta):
    table = {}
    for byte_value in range(256):
        bits = bytes_to_bits([byte_value])
        coefficients = sample_poly_cbd(bits, eta, num_coefficients=2, verbose=False)
        table[byte_value] = coefficients
    return table


# lookup_coefficients: instead of recalculating, just look each byte up
# in the pre-built table
def lookup_coefficients(byte_sequence, table):
    coefficients = []
    for byte_value in byte_sequence:
        coefficients.extend(table[byte_value])
    return coefficients


if __name__ == "__main__":
    # change these bytes and re-run to see completely different coefficients
    example_bytes = bytes([13, 201, 7, 255])
    print("example bytes =", list(example_bytes))

    bits = bytes_to_bits(example_bytes)
    print("bits            =", bits)
    print()

    eta = 2
    coefficients = sample_poly_cbd(bits, eta, num_coefficients=8)
    print()
    print(f"all coefficients (eta={eta}) =", coefficients)

    print()
    print("--- now using the lookup table instead ---")
    table = build_cbd_table(eta)
    table_coefficients = lookup_coefficients(example_bytes, table)
    print("table-based coefficients =", table_coefficients)
    print("matches direct calculation:", table_coefficients == coefficients)
