import os

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

WIDTH, HEIGHT = A4
MARGIN = 2 * cm
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "act_3_explained.pdf")

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
heading("Act 3: Bob's Decapsulate")
body("Bob receives c and nothing else. He has to do two separate jobs:")
gap(0.25 * cm)
body("1. work out the shared secret", indent=0.5 * cm)
body("2. prove the ciphertext was built honestly, and not crafted by an attacker", indent=0.5 * cm)
gap(0.3 * cm)
body("Job 2 is the one that matters for security, and it takes most of the Act.")
gap(0.5 * cm)

# --- Act 3 flow diagram ---
bw, bh = 3.5 * cm, 1 * cm
lx = MARGIN + 1 * cm
t = y

box(lx, t, bw, bh, "c", "received")
arrow(lx + bw / 2, t - bh, lx + bw / 2, t - bh - 0.8 * cm, "open + use S")

t2 = t - bh - 0.8 * cm
box(lx, t2, bw, bh, "m_recovered", "his guess at m")
arrow(lx + bw / 2, t2 - bh, lx + bw / 2, t2 - bh - 0.8 * cm, "sha3_512")

t3 = t2 - bh - 0.8 * cm
box(lx, t3, bw, bh, "K_prime + r_coins_prime", "")
arrow(lx + bw / 2, t3 - bh, lx + bw / 2, t3 - bh - 0.8 * cm, "redo ALL of Act 2")

t4 = t3 - bh - 0.8 * cm
box(lx, t4, bw, bh, "c_prime", "his rebuilt version")

# comparison box on the right
rx = MARGIN + 8 * cm
box(rx, t4, bw, bh, "c", "the real one", dashed=True)
arrow(lx + bw, t4 - bh / 2, rx, t4 - bh / 2, "same?")

t5 = t4 - bh - 1 * cm
c.setFont("Helvetica-Bold", 9)
c.drawString(MARGIN + 1 * cm, t5, "YES  ->  K_final = K_prime          (the real shared secret)")
t5 -= 0.5 * cm
c.drawString(MARGIN + 1 * cm, t5, "NO   ->  K_final = hash(zed + c)    (the imposter, quietly)")

y = t5 - 0.8 * cm

new_page()

heading("Act 3 step by step")

sub("Step 0 - open the ciphertext")
mono("u_received, v_received = ciphertext_opener(c)")
body("WHAT: unpack c back into working numbers.")
body("HOW: slice the blob apart, byte_decode each piece, then decompress.")
gap(0.2 * cm)
body("IMPORTANT: what comes out is CLOSE to Alice's u and v but NOT identical. Compression")
body("threw detail away on the way out and it cannot be recovered. The code prints this")
body("explicitly and it shows False - which is correct and expected, not a bug.")

gap(0.5 * cm)
sub("Step 1 - recover the message")
mono("w = v_received - (S . u_received)")
body("WHAT: undo the maths to get back to something close to m_encoded.")
body("HOW: remember what v was built from:")
gap(0.2 * cm)
mono("v = b.r + e_two + m_encoded        and        b = A.S + e")
gap(0.2 * cm)
body("so v contains (A.S).r hidden inside it. And u = A_t.r + e_one, so S.u gives back")
body("roughly that same (A.S).r term. Subtracting one from the other cancels the big")
body("shared part and leaves m_encoded plus a small pile of leftover noise.")
gap(0.3 * cm)
body("Bob is the only person who can do this, because it needs S.")

gap(0.4 * cm)
sub("Step 1b - turning w back into bits")
mono("zero_check = min(abs(w[i] - 0), abs(w[i] - q))")
mono("half_check = abs(w[i] - q // 2)")
mono("if half_check > zero_check:  bit is 0    else:  bit is 1")
body("WHAT: decide, for each of the 256 positions, whether it was a 0 or a 1.")
body("HOW: each number should be sitting near either 0 or near halfway (1665). Measure how")
body("far it is from each, and go with whichever is closer.")
gap(0.2 * cm)
body("The min() on zero_check handles wraparound - a value like 3320 is only 9 away from 0")
body("going the other way round, so it counts as near zero, not near the top.")
gap(0.2 * cm)
body("THIS IS WHY THE NOISE CAN BE TOLERATED: the gap between 0 and 1665 is enormous.")
body("The noise would have to stack up over 800 in one direction to push a value across")
body("the halfway line and flip the answer. The published odds of that happening for")
body("ML-KEM-1024 are about 2^-174.")

new_page()

heading("Act 3 step by step (continued)")

sub("Step 2 - re-hash")
mono("g_output_bob = sha3_512(byte_encode(m_recovered, 1) + H(ek))")
mono("K_prime       = g_output_bob[0:32]")
mono("r_coins_prime = g_output_bob[32:64]")
body("WHAT: exactly what Alice did in Act 2, but starting from m_recovered.")
body("HOW: same hash, same split. Bob reuses his STORED H(ek) from Act 1 rather than")
body("recomputing it.")
gap(0.2 * cm)
body("If m_recovered really is Alice's m, then K_prime will be identical to her K, because")
body("the same input through the same hash always gives the same output.")

gap(0.4 * cm)
sub("Step 3 - regenerate the noise")
body("WHAT: rebuild r', e_one', e_two' from r_coins_prime.")
body("HOW: the same position-tagged shake_256 and CBD table trick. Nothing new.")
gap(0.2 * cm)
body("This only works because Alice DERIVED her noise from her message rather than picking")
body("it independently. That decision back in Act 2 is what makes this whole check possible.")

gap(0.4 * cm)
sub("Step 4 - rebuild the ciphertext")
mono("u_prime = A_t . r' + e_one'")
mono("v_prime = b_t . r' + e_two' + m_recovered_encoded")
body("WHAT: redo Alice's entire encryption, from Bob's side.")
body("HOW: identical formulas. Bob uses his OWN A (he had the real one all along, no need")
body("to rebuild from rho) and his own b.")
gap(0.2 * cm)
body("m_recovered_encoded uses the same (q+1)//2 = 1665 rounding Alice used. It has to")
body("match hers exactly or the rebuilt ciphertext would never line up.")

gap(0.4 * cm)
sub("Steps 5 and 6 - the integrity check")
mono("c_prime = ciphertext_maker(u_prime, v_prime)")
mono("ciphertext_matches = (c_prime == c)")
body("WHAT: the actual security check of the whole scheme.")
gap(0.25 * cm)
body("WHY NOT JUST COMPARE u_prime TO u: because compression is lossy, those would never")
body("match exactly even when everything is perfectly fine.")
gap(0.25 * cm)
body("THE FIX: run u_prime and v_prime through the SAME compress-and-pack steps Alice used,")
body("producing Bob's own c_prime, then compare the finished bytes. Both sides go through")
body("identical lossy steps, and lossiness is deterministic - the same input always gives")
body("the same output - so an honest message produces byte-for-byte identical ciphertexts.")

new_page()

heading("Why the check exists at all")

body("It is tempting to think Bob only needs to recover a message and that is that. He does")
body("not, and the reason is worth being clear about.")
gap(0.4 * cm)

sub("Decoding never fails")
body("Feed the decode maths ANY u and v - real, fake, complete garbage - and it will always")
body("hand back some 256-bit result. There is no such thing as a ciphertext that does not")
body("decode. So checking whether a message came out is a test that is always true, and")
body("therefore tests nothing at all.")

gap(0.5 * cm)
sub("What the check actually proves")
body("Not that something decoded, but that the ciphertext was HONESTLY BUILT - by someone")
body("who genuinely knew the message and followed the whole process properly.")
gap(0.25 * cm)
body("An attacker can craft a u and v pair that was never produced by encrypting anything,")
body("purely to probe Bob's secret S. That fake pair still decodes to some message. Without")
body("the rebuild-and-compare check, Bob would have no way of ever noticing, and repeated")
body("probes could slowly leak information about S.")
gap(0.25 * cm)
body("Redoing the entire encryption and comparing is the one step that closes that off.")

gap(0.6 * cm)
sub("The two endings")
gap(0.3 * cm)

body("PASS:")
mono("K_final = K_prime")
body("The confirmed shared secret. Identical to Alice's K.", indent=0.4 * cm)

gap(0.3 * cm)
body("FAIL:")
mono("imposter_protocol = zed + c")
mono("K_final = shake_256(imposter_protocol).digest(32)")
body("A decoy key, built from Bob's private zed and the ciphertext he actually received.", indent=0.4 * cm)

gap(0.4 * cm)
body("The decoy is a normal-looking 32 bytes and flows into Act 4 exactly like a real key.")
body("Nothing downstream knows or cares which branch produced it.")
gap(0.25 * cm)
body("WHY BOTHER: if Bob visibly errored on a bad ciphertext, an attacker could send")
body("thousands of probes and learn from which ones failed. Because he behaves identically")
body("either way, there is nothing to observe. The rejection is silent.")
gap(0.25 * cm)
body("The attacker cannot predict the decoy either, since zed is private. So a tampered")
body("message simply leads to Alice and Bob holding different keys - the conversation")
body("quietly fails and they would need to start a fresh exchange.")

gap(0.5 * cm)
sub("End of Act 3")
body("Bob holds K_final. Nothing has been sent back to Alice - Decapsulate replies to")
body("nobody. Both sides now independently hold what should be the same 32 bytes, and")
body("that value was never transmitted in either direction.")

c.save()
print("saved to", OUT_PATH)
