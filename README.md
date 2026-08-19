# ML-KEM-1024 (Kyber) — From-Scratch Implementation

A from-scratch Python implementation of **ML-KEM-1024**, the post-quantum key
encapsulation mechanism standardised by NIST in **FIPS 203**, built as part of an
MSc dissertation.

Everything is written from first principles — no cryptographic libraries are used
for any part of the KEM itself. Only Python's built-in `hashlib` (for SHA-3 and
SHAKE) and `secrets` (for randomness) are relied upon.

## Parameters

Real ML-KEM-1024 scale throughout:

| Parameter | Value | Meaning |
|---|---|---|
| `n` | 256 | coefficients per polynomial |
| `q` | 3329 | modulus |
| `k` | 4 | matrix/vector dimension |
| `eta` | 2 | noise bound (CBD) |
| `du` / `dv` | 11 / 5 | compression widths |

Key and ciphertext sizes match **FIPS 203 Table 3** exactly:

- encapsulation key: **1568 bytes**
- ciphertext: **1568 bytes**
- shared secret: **32 bytes**

## Main file

**`Kyber-1024-ML-KEM_FIPS-203_V5.py`** — the complete implementation.

It is laid out as a setup section followed by four acts:

- **Setup** — polynomial arithmetic, the NTT toolkit, the CBD table, rejection
  sampling, byte encoding/decoding, and compression
- **Act 1** — KeyGen
- **Act 2** — Encapsulate
- **Act 3** — Decapsulate, including the re-encryption check and implicit rejection
- **Act 4** — arranging the resulting shared secret into the AES-256 key layout

Run it with:

```bash
python3 "Kyber-1024-ML-KEM_FIPS-203_V5.py"
```

## What is implemented

- Rejection sampling to build the matrix `A` from a 32-byte seed
- Centered binomial distribution sampling via an explicit 256-entry lookup table
- **Number-Theoretic Transform** multiplication using the FIPS 203 Appendix A
  tables — roughly 7× faster than schoolbook multiplication at this scale
- `ByteEncode` / `ByteDecode` bit-packing at widths 1, 5, 11 and 12
- Ciphertext compression and decompression
- The Fujisaki–Okamoto transform: re-encryption check with **implicit rejection**
  (a private fallback value produces a decoy key on failure, so rejection is
  indistinguishable from success)

## Development history

Earlier files are kept to show how the implementation was built up:

| File | Stage |
|---|---|
| `Hashing_kyber_CBD_V2.py` | schoolbook multiplication, seeded generation |
| `Kyber-1024_NTT_V3.py` | NTT multiplication swapped in |
| `compression_V4.py` | compression developed and tested standalone |
| `Kyber-1024-ML-KEM_FIPS-203_V5.py` | **current** — compression integrated |

Supporting standalone tests: `NTT_Multiplication_v2.py`, `byte_encode_test.py`,
`NTT_n256_full_trace.py`.

## Documentation

The `build_*_pdf.py` scripts generate explanatory PDFs covering the setup section,
each act, and the NTT in detail — including worked hand-calculations at both a
reduced scale (n=8) and real scale (n=256).

## Known simplifications

Deliberate deviations from the letter of FIPS 203, none of which affect
correctness of the exchange:

1. `rho` and `sigma` are generated as two independent random seeds rather than
   derived together from a single seed via `G(d ‖ k)`
2. Input and key validation checks (type, range, and hash checks on received keys)
   are not implemented
3. The message `m` is generated as 256 individual random bits rather than as
   32 random bytes

## Status

The KEM itself — KeyGen, Encapsulate and Decapsulate — is complete and verified.
The AES-256 layer beyond the key layout (key schedule and cipher) is not
implemented here.

## Disclaimer

This is an educational implementation written to demonstrate understanding of the
standard. It is **not constant-time**, has not been audited, and must not be used
to protect real data.
