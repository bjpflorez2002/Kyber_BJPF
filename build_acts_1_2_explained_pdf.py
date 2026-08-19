import os

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

WIDTH, HEIGHT = A4
MARGIN = 2 * cm
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "acts_1_and_2_explained.pdf")

c = canvas.Canvas(OUT_PATH, pagesize=A4)
y = HEIGHT - MARGIN


def new_page():
    global y
    c.showPage()
    y = HEIGHT - MARGIN


def ensure(needed):
    global y
    if y - needed < MARGIN:
        new_page()


def heading(text, size=15):
    global y
    ensure(1.3 * cm)
    c.setFont("Helvetica-Bold", size)
    c.drawString(MARGIN, y, text)
    y -= 0.5 * cm
    c.line(MARGIN, y, WIDTH - MARGIN, y)
    y -= 0.5 * cm


def sub(text):
    global y
    ensure(0.9 * cm)
    c.setFont("Helvetica-Bold", 11.5)
    c.drawString(MARGIN, y, text)
    y -= 0.5 * cm


def body(text, size=10, leading=13.5, indent=0):
    global y
    ensure(leading + 2)
    c.setFont("Helvetica", size)
    c.drawString(MARGIN + indent, y, text)
    y -= leading


def mono(text, size=9, leading=12, indent=0.4 * cm):
    global y
    ensure(leading + 2)
    c.setFont("Courier", size)
    c.drawString(MARGIN + indent, y, text)
    y -= leading


def gap(a=0.3 * cm):
    global y
    y -= a


def box(x, top, w, h, label, sublabel="", dashed=False):
    if dashed:
        c.setDash(2, 2)
    c.roundRect(x, top - h, w, h, 4, stroke=1, fill=0)
    c.setDash()
    c.setFont("Helvetica-Bold", 8.5)
    c.drawCentredString(x + w / 2, top - h / 2 + (3.5 if sublabel else -2.5), label)
    if sublabel:
        c.setFont("Helvetica", 7)
        c.drawCentredString(x + w / 2, top - h / 2 - 7, sublabel)


def arrow(x1, y1, x2, y2, label=""):
    import math
    c.line(x1, y1, x2, y2)
    ang = math.atan2(y2 - y1, x2 - x1)
    for s in (-0.4, 0.4):
        c.line(x2, y2, x2 - 6 * math.cos(ang + s), y2 - 6 * math.sin(ang + s))
    if label:
        c.setFont("Helvetica-Oblique", 7.5)
        c.drawCentredString((x1 + x2) / 2, (y1 + y2) / 2 + 4, label)


# =================================================================
heading("Act 1: Bob's KeyGen")
body("Bob builds his key pair. Nothing has been sent yet and Alice does not exist as far")
body("as this Act is concerned. At the end of it Bob has something he can publish, and")
body("several things he must never let go of.")
gap(0.5 * cm)

# --- Act 1 flow diagram ---
bw, bh = 3.3 * cm, 1 * cm
lx = MARGIN + 0.3 * cm
rx = MARGIN + 8.5 * cm
t = y

box(lx, t, bw, bh, "rho", "32 random bytes")
box(rx, t, bw, bh, "sigma", "32 random bytes")
arrow(lx + bw / 2, t - bh, lx + bw / 2, t - bh - 0.85 * cm, "rejection sampling")
arrow(rx + bw / 2, t - bh, rx + bw / 2, t - bh - 0.85 * cm, "CBD table")

t2 = t - bh - 0.85 * cm
box(lx, t2, bw, bh, "A", "4x4 matrix")
box(rx, t2, bw, bh, "S  and  e", "small values")

midx = (lx + bw / 2 + rx + bw / 2) / 2
c.line(lx + bw / 2, t2 - bh - 0.5 * cm, rx + bw / 2, t2 - bh - 0.5 * cm)
c.line(lx + bw / 2, t2 - bh, lx + bw / 2, t2 - bh - 0.5 * cm)
c.line(rx + bw / 2, t2 - bh, rx + bw / 2, t2 - bh - 0.5 * cm)
arrow(midx, t2 - bh - 0.5 * cm, midx, t2 - bh - 1.05 * cm, "b = A.S + e")

t3 = t2 - bh - 1.05 * cm
box(midx - bw / 2, t3, bw, bh, "b", "the public value")
y = t3 - bh - 0.8 * cm

gap(0.2 * cm)
body("Separately, zed (32 random bytes) is generated and put straight in the drawer -")
body("it does nothing at all until Act 3, and only then if something has gone wrong.")

new_page()

heading("Act 1 step by step")

sub("Step 1 - rho")
mono("rho = secrets.token_bytes(32)")
body("WHAT: 32 random bytes.")
body("HOW: secrets, not random - this has to be genuinely unguessable, not merely")
body("statistically random.")
body("WHY IT MATTERS: this tiny seed gets shared INSTEAD of the whole matrix. A is 16")
body("polynomials of 256 numbers each - 6144 bytes if you sent it raw. rho is 32 bytes.")
body("That is 192 times smaller, and anyone holding rho can rebuild A exactly.")

gap(0.4 * cm)
sub("Step 2 - A, the matrix")
mono("cell_seed = rho + bytes([row_num, col_num])")
mono("poly = poly_generator_from_seed(cell_seed)")
body("WHAT: a 4x4 matrix where every cell is a full 256-coefficient polynomial.")
body("HOW: for each cell, take rho and stick that cell's row and column on the end as a")
body("tag. Feed that tagged seed to the rejection sampler.")
body("THE TRICK: one seed makes 16 completely different polynomials, because each cell")
body("gets a different tag. Cell (0,0) and cell (0,1) start from almost identical seeds,")
body("but hashing makes the two outputs completely unrelated.")

gap(0.4 * cm)
sub("Step 3 - zed")
mono("zed = secrets.token_bytes(32)")
body("WHAT: 32 random bytes, Bob's hidden backup value.")
body("HOW: same as rho.")
body("WHY: absolutely nothing happens with it here. It waits in Bob's private key until")
body("Act 3, and only gets touched if a ciphertext check fails.")

gap(0.4 * cm)
sub("Step 4 - sigma, then S and e")
mono("sigma = secrets.token_bytes(32)")
mono("S uses positions 0,1,2,3")
mono("e carries on with positions 4,5,6,7")
body("WHAT: S is Bob's private secret (4 polynomials), e is noise (4 polynomials).")
body("HOW: the same tagging trick as A, but tagged with a plain counter instead of row and")
body("column. Uses shake_256 and the CBD table rather than rejection sampling, because")
body("these need to be TINY (-2 to +2), not spread over the whole range.")
body("WORTH NOTICING: S takes positions 0 to 3, then e simply CARRIES ON counting from 4")
body("to 7. One seed, one counter, 8 different polynomials, no second seed needed.")

new_page()

heading("Act 1 step by step (continued)")

sub("Step 5 - b = A.S + e")
mono("dot_product = poly_add(dot_product, ntt_multiply(row[i], S[i]))")
mono("b.append(poly_add(dot_product, e[row_num]))")
body("WHAT: the actual public key value.")
body("HOW: a standard matrix times vector. For each row of A, multiply each entry by the")
body("matching entry of S, add all four together, then add that row's noise from e.")
gap(0.3 * cm)
body("WHY THIS IS THE ENTIRE SECURITY: given A and b, working backwards to find S is the")
body("hard lattice problem. Without the noise e it would be ordinary school algebra and")
body("anyone could solve it. The noise is what makes it hard - and it is small enough that")
body("the message still decodes correctly at the other end.")

gap(0.5 * cm)
sub("Step 6 - H(ek)")
mono("b_encoded = b''.join(byte_encode(poly, 12) for poly in b)")
mono("combined_bytes = rho + b_encoded")
mono("H(ek) = sha3_256(combined_bytes)")
body("WHAT: a 32-byte fingerprint of Bob's own public key.")
body("HOW: byte-encode b at 12 bits per coefficient, stick rho on the front, hash once.")
body("WHY: worked out once and kept. Alice independently computes the identical value in")
body("Act 2, and Bob reuses his stored copy in Act 3 rather than recomputing it.")

gap(0.6 * cm)
sub("End of Act 1 - what is public and what is not")
gap(0.2 * cm)

col1, col2 = MARGIN + 0.5 * cm, MARGIN + 8 * cm
c.setFont("Helvetica-Bold", 10)
c.drawString(col1, y, "PUBLIC - this is (rho, b)")
c.drawString(col2, y, "PRIVATE - never leaves Bob")
y -= 0.4 * cm
c.line(MARGIN + 0.5 * cm, y + 0.1 * cm, WIDTH - MARGIN, y + 0.1 * cm)
y -= 0.2 * cm
c.setFont("Helvetica", 10)
pairs = [("rho  (32 bytes)", "S     - the secret"),
         ("b    (4 polynomials)", "e     - the noise"),
         ("", "sigma - the seed they came from"),
         ("", "zed   - the backup"),
         ("", "H(ek) - the stored fingerprint")]
for a, bb in pairs:
    c.drawString(col1, y, a)
    c.drawString(col2, y, bb)
    y -= 0.45 * cm

new_page()

# =================================================================
heading("Act 2: Alice's Encapsulate")
body("Alice receives (rho, b) and nothing else. From that alone she produces two things:")
body("a shared secret only she knows so far, and one ciphertext to send back.")
gap(0.5 * cm)

# --- Act 2 flow diagram ---
t = y
bw2, bh2 = 3.4 * cm, 1 * cm
cx = MARGIN + 5.8 * cm

box(MARGIN + 0.3 * cm, t, bw2, bh2, "(rho, b)", "received from Bob")
arrow(MARGIN + 0.3 * cm + bw2, t - bh2 / 2, MARGIN + 5.5 * cm, t - bh2 / 2, "rebuild")
box(MARGIN + 5.5 * cm, t, bw2, bh2, "Alice_A + Alice_HEK", "same as Bob's")

t2 = t - bh2 - 0.9 * cm
box(MARGIN + 0.3 * cm, t2, bw2, bh2, "m", "256 random bits")
arrow(MARGIN + 0.3 * cm + bw2, t2 - bh2 / 2, MARGIN + 5.5 * cm, t2 - bh2 / 2, "sha3_512")
box(MARGIN + 5.5 * cm, t2, bw2, bh2, "K  +  r_coins", "64 bytes, split in half")

t3 = t2 - bh2 - 0.9 * cm
arrow(MARGIN + 5.5 * cm + bw2 / 2, t2 - bh2, MARGIN + 5.5 * cm + bw2 / 2, t3, "CBD table")
box(MARGIN + 5.5 * cm, t3, bw2, bh2, "r, e_one, e_two", "the noise")

t4 = t3 - bh2 - 0.9 * cm
arrow(MARGIN + 5.5 * cm + bw2 / 2, t3 - bh2, MARGIN + 5.5 * cm + bw2 / 2, t4)
box(MARGIN + 5.5 * cm, t4, bw2, bh2, "u  and  v", "")

t5 = t4 - bh2 - 0.9 * cm
arrow(MARGIN + 5.5 * cm + bw2 / 2, t4 - bh2, MARGIN + 5.5 * cm + bw2 / 2, t5, "compress + pack")
box(MARGIN + 5.5 * cm, t5, bw2, bh2, "c", "1568 bytes, SENT")

y = t5 - bh2 - 0.8 * cm
gap(0.2 * cm)
body("K never moves. It stays on Alice's side. Only c is sent.")

new_page()

heading("Act 2 step by step")

sub("Step 1 - Alice_A")
body("WHAT: Alice rebuilds Bob's matrix herself.")
body("HOW: identical loop to Act 1 - same rho, same row and column tags, same rejection")
body("sampler. She was never sent the matrix, only the seed it came from.")

gap(0.4 * cm)
sub("Step 2 - Alice_HEK")
body("WHAT: Alice works out the same public-key fingerprint Bob already stored.")
body("HOW: byte-encode b, stick rho on the front, sha3_256. Exactly what Bob did.")
body("WHY: it binds everything that follows to this specific public key. Without it, the")
body("shared secret would not be tied to this particular exchange.")

gap(0.4 * cm)
sub("Step 3 - m, the message")
mono("m.append(secrets.choice([0, 1]))   x 256")
body("WHAT: 256 random bits. This is the ONLY genuinely fresh randomness in Act 2.")
body("HOW: secrets again, because everything downstream is derived from this.")
body("WORTH KNOWING: m is not a message in the ordinary sense. Nobody wants to read it.")
body("Its whole job is to be random and to be recoverable by Bob later.")

gap(0.4 * cm)
sub("Step 4 - K and r_coins")
mono("m_bytes = byte_encode(m, 1)          -> 32 bytes")
mono("g_output = sha3_512(m_bytes + Alice_HEK)  -> 64 bytes")
mono("K       = g_output[0:32]")
mono("r_coins = g_output[32:64]")
body("WHAT: one hash, cut clean down the middle.")
body("HOW: pack m into bytes (d=1, so 8 bits per byte), glue Alice_HEK on, hash once with")
body("sha3_512 which always gives back exactly 64 bytes, then split.")
body("K       - the real shared secret. Alice sets it aside and sends it nowhere.")
body("r_coins - a seed, used immediately to make the noise for this encryption.")
gap(0.2 * cm)
body("THIS IS THE CLEVER PART: the noise is DERIVED from the message rather than picked")
body("independently. That is what lets Bob later redo the whole thing from scratch and")
body("check that the ciphertext was built honestly.")

new_page()

heading("Act 2 step by step (continued)")

sub("Step 5 - r, e_one, e_two")
mono("r     takes positions 0..3")
mono("e_one carries on 4..7")
mono("e_two takes position 8")
body("WHAT: the noise for this one encryption.")
body("HOW: the same one-seed-plus-counter trick used for S and e in Act 1, just seeded")
body("from r_coins instead of sigma. Same shake_256 and CBD table.")

gap(0.4 * cm)
sub("Step 6 - m_encoded")
mono("m_encoded.append(((q + 1) // 2) * m[i])")
body("WHAT: turns each bit of m into a real number - either 0 or 1665.")
body("HOW: q is 3329, an odd number, so half of it is 1664.5. Rounding to nearest gives")
body("1665, which is what (q+1)//2 produces.")
body("WHY 1665 AND NOT 0 AND 1: spreading the two possible values as far apart as possible")
body("gives the noise maximum room to wobble without ever flipping the answer.")

gap(0.4 * cm)
sub("Step 7 - A_t and b_t")
body("A_t is the transpose of Alice_A - rows become columns.")
body("b_t is literally just b. Transposing a vector does nothing, so it is a no-op.")

gap(0.4 * cm)
sub("Step 8 - u and v")
mono("u = A_t x r + e_one")
mono("v = b_t . r + e_two + m_encoded")
body("WHAT: the two mathematical values that carry the message.")
body("HOW: same matrix and vector maths as Act 1, using ntt_multiply.")
gap(0.2 * cm)
body("u - carries no message, it is what lets Bob undo the maths using his secret S.")
body("v - carries the actual message, hidden underneath noise and the b.r term.")

gap(0.4 * cm)
sub("Step 9 - c, the ciphertext")
mono("c = ciphertext_maker(u, v)")
body("WHAT: the single blob that actually gets sent.")
body("HOW: compress u to 11 bits and v to 5 bits, byte-encode both, glue together.")
body("1408 + 160 = 1568 bytes, matching FIPS 203 Table 3 exactly.")
gap(0.3 * cm)
body("END OF ACT 2: Alice holds K privately. Bob has been sent c and nothing else.")
body("Neither the key nor the message ever travelled.")

c.save()
print("saved to", OUT_PATH)
