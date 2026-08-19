import secrets
import hashlib

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# this is the library doing the heavy lifting - AESGCM handles the key schedule,
# all 14 rounds, and the tamper-check tag, all internally. we just hand it a key


# =================================================================
# pretending we just finished the kyber exchange
# =================================================================

# K_final - in the real thing this comes out of Act 3. here im just making one
# the same way (32 random bytes) so this file runs on its own
K_final = secrets.token_bytes(32)

print("K_final (our AES-256 key) =", K_final.hex())
print("length:", len(K_final), "bytes - exactly what AES-256 wants")


# =================================================================
# alice encrypts a message
# =================================================================
print()
print("=== alice sends a message ===")

message = b"hey cousin, this is a real message over a quantum-safe channel"
print("alices message:", message)

# nonce - 12 fresh random bytes, EVERY single message needs its own.
# not secret, it gets sent in the clear, it just has to never repeat
nonce = secrets.token_bytes(12)
print("nonce:", nonce.hex())

alice_cipher = AESGCM(K_final)
encrypted = alice_cipher.encrypt(nonce, message, None)

print("encrypted:", encrypted.hex())
print("encrypted length:", len(encrypted), "bytes (message was", len(message), "bytes + 16 byte tamper-check tag)")

# what actually goes over the wire - nonce stuck on the front of the ciphertext
transmission = nonce + encrypted
print()
print("what alice actually sends:", len(transmission), "bytes")


# =================================================================
# bob decrypts it - the normal case, he has the real key
# =================================================================
print()
print("=== bob decrypts, normal case (he has the real key) ===")

# bob splits the nonce back off the front
bob_nonce = transmission[0:12]
bob_encrypted = transmission[12:]

bob_cipher = AESGCM(K_final)
decrypted = bob_cipher.decrypt(bob_nonce, bob_encrypted, None)

print("bob decrypted:", decrypted)
print("does it match what alice sent:", decrypted == message)


# =================================================================
# now the interesting bit - what if bob ended up with the IMPOSTER key
# =================================================================
print()
print("=== bob decrypts, but with the imposter key from Act 3 ===")

# pretending bobs ciphertext check failed, so he built K_final from zed instead
zed = secrets.token_bytes(32)
imposter_protocol = zed + b"some tampered ciphertext"
K_final_imposter = hashlib.shake_256(imposter_protocol).digest(32)

print("bobs imposter key =", K_final_imposter.hex())
print("(completely different to alices key, and alice has no idea it exists)")
print()

bob_imposter_cipher = AESGCM(K_final_imposter)
try:
    bob_imposter_cipher.decrypt(bob_nonce, bob_encrypted, None)
    print("decrypted fine - this should NOT happen")
except Exception as failure:
    print("decryption FAILED, error type:", type(failure).__name__)
    print("this is AES-GCM catching it - the tamper-check tag doesnt add up,")
    print("so it refuses to hand back garbage and raises an error instead")
