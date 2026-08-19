import secrets

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# the shared key from the kyber exchange - both bob and alice have this
K_final = secrets.token_bytes(32)


# --- bob sends ---
message = b"hello alice, im Gay jfoerwqijre302rj9043e9qdwj8jansdiocmokedl,s;xc.d/sc/[ [/[csdpxk o]]]"
nonce = secrets.token_bytes(12)
encrypted = AESGCM(K_final).encrypt(nonce, message, None)

print("bob sends:", (nonce + encrypted).hex())


# --- alice reads ---
decrypted = AESGCM(K_final).decrypt(nonce, encrypted, None)

print("alice reads:", decrypted)
