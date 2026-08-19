import os

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

WIDTH, HEIGHT = A4
MARGIN = 2 * cm
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "setup_explained.pdf")

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
heading("The Setup Section - Every Tool Explained")
body("Setup is everything that gets defined BEFORE anything actually happens. Nothing here")
body("is Bob or Alice doing something - it is purely the toolbox they both reach into later.")
body("It splits into 6 groups.")
gap(0.5 * cm)

# --- overview diagram: the 6 groups ---
gw, gh = 5 * cm, 1.15 * cm
gx1, gx2, gx3 = MARGIN, MARGIN + 5.6 * cm, MARGIN + 11.2 * cm
top = y

box(gx1, top, gw, gh, "1. THE THREE NUMBERS", "n, q, k")
box(gx2, top, gw, gh, "2. BASIC POLY MATHS", "add, sub, mult")
row2 = top - 1.5 * cm
box(gx1, row2, gw, gh, "3. THE NTT TOOLKIT", "the fast multiply")
box(gx2, row2, gw, gh, "4. SMALL RANDOM NUMBERS", "CBD table")
row3 = row2 - 1.5 * cm
box(gx1, row3, gw, gh, "5. BIG RANDOM NUMBERS", "rejection sampling")
box(gx2, row3, gw, gh, "6. BYTE PACKING + COMPRESSION", "getting ready to send")

y = row3 - gh - 0.8 * cm

gap(0.2 * cm)
body("Groups 1-2 are the foundations. Group 3 replaced the slow multiply. Groups 4-5 build")
body("the random values everything is made from. Group 6 turns numbers into things you can")
body("actually send over a wire.")

new_page()

# =================================================================
heading("Group 1: The Three Numbers")
mono("n = 256      q = 3329      k = 4")
gap(0.3 * cm)
body("n - how many coefficients live in each polynomial. Every polynomial in this whole")
body("   project is a list of exactly 256 numbers.")
gap(0.15 * cm)
body("q - the modulus. Every single number stays between 0 and 3328. Anything that goes")
body("   over wraps back round, which is what all the % q you see everywhere is doing.")
gap(0.15 * cm)
body("k - the matrix and vector size. A is k x k (so 4x4), and S, e, b, u are all k long.")
body("   This one number is what makes it ML-KEM-1024 rather than 512 or 768.")

gap(0.6 * cm)
heading("Group 2: Basic Polynomial Maths")

sub("poly_add(f, g) and poly_sub(f, g)")
body("WHAT: add or subtract two polynomials.")
body("HOW: walk along both lists position by position, add (or subtract) the two numbers")
body("sitting at each position, wrap the answer with % q. Nothing clever.")
gap(0.3 * cm)
mono("position 0:  f[0] + g[0]  mod q")
mono("position 1:  f[1] + g[1]  mod q")
mono("...and so on for all 256")

gap(0.5 * cm)
sub("poly_mult(f, g)  -  the OLD slow way, no longer used")
body("WHAT: multiplies two polynomials the obvious schoolbook way.")
body("HOW: two nested loops. Every number in f gets multiplied by every number in g, and")
body("each result is dropped into a bin decided by adding the two positions together.")
body("That gives 511 slots, which is too many, so anything sitting at position 256 or")
body("higher gets folded back down and SUBTRACTED (because x^n = -1 in this ring).")
gap(0.3 * cm)
body("Cost: 256 x 256 = about 65,000 multiplications. This is why NTT exists.")
body("It is kept in the file purely as a reference to check the NTT answer against.")

new_page()

# =================================================================
heading("Group 3: The NTT Toolkit")
body("This is what replaced poly_mult. Same answers, roughly 7x faster in practice.")
gap(0.4 * cm)

sub("The three lookup tables")
body("zeta - 128 fixed numbers copied straight out of FIPS 203 Appendix A. NOT calculated")
body("   by us. They are all powers of 17 mod 3329, but in a scrambled order (bit-reversal)")
body("   that we deliberately take as given rather than derive.")
gap(0.15 * cm)
body("zeta_reverse - that exact same list flipped end to end, so the reverse transform can")
body("   walk forwards through it instead of having to walk zeta backwards.")
gap(0.15 * cm)
body("gamma - a SEPARATE 128 numbers, also from Appendix A. Used only in the multiply step,")
body("   never in the transform.")

gap(0.5 * cm)
sub("The pipeline")
gap(0.3 * cm)

bw, bh = 3.2 * cm, 1.1 * cm
lx, rx = MARGIN + 0.5 * cm, MARGIN + 9 * cm
t = y
box(lx, t, bw, bh, "f", "256 numbers")
box(rx, t, bw, bh, "g", "256 numbers")
arrow(lx + bw / 2, t - bh, lx + bw / 2, t - bh - 0.9 * cm)
arrow(rx + bw / 2, t - bh, rx + bw / 2, t - bh - 0.9 * cm)
c.setFont("Helvetica-Oblique", 7.5)
c.drawString(lx + bw / 2 + 0.2 * cm, t - bh - 0.55 * cm, "hat_maker")
c.drawString(rx + bw / 2 + 0.2 * cm, t - bh - 0.55 * cm, "hat_maker")

t2 = t - bh - 0.9 * cm
box(lx, t2, bw, bh, "f_hat", "transformed")
box(rx, t2, bw, bh, "g_hat", "transformed")

midx = (lx + bw / 2 + rx + bw / 2) / 2
c.line(lx + bw / 2, t2 - bh - 0.5 * cm, rx + bw / 2, t2 - bh - 0.5 * cm)
c.line(lx + bw / 2, t2 - bh, lx + bw / 2, t2 - bh - 0.5 * cm)
c.line(rx + bw / 2, t2 - bh, rx + bw / 2, t2 - bh - 0.5 * cm)
arrow(midx, t2 - bh - 0.5 * cm, midx, t2 - bh - 1.1 * cm)
c.setFont("Helvetica-Oblique", 7.5)
c.drawString(midx + 0.2 * cm, t2 - bh - 0.85 * cm, "c_hat_maker (uses gamma)")

t3 = t2 - bh - 1.1 * cm
box(midx - bw / 2, t3, bw, bh, "c_hat", "combined")
arrow(midx, t3 - bh, midx, t3 - bh - 0.9 * cm)
c.setFont("Helvetica-Oblique", 7.5)
c.drawString(midx + 0.2 * cm, t3 - bh - 0.55 * cm, "NTT_final (uses zeta_reverse)")

t4 = t3 - bh - 0.9 * cm
box(midx - bw / 2, t4, bw, bh, "answer", "f x g")
y = t4 - bh - 0.7 * cm

new_page()

# =================================================================
heading("Group 3 continued: How each NTT function works")

sub("hat_maker(f)  -  the forward transform")
body("WHAT: turns a normal polynomial into its transformed (hat) shape.")
body("HOW: 7 rounds. Each round cuts the list into twice as many equal groups as the round")
body("before, and halves the pairing distance. Every group grabs the next unused zeta.")
gap(0.3 * cm)

# rounds table
cols = [MARGIN + 0.4 * cm, MARGIN + 3 * cm, MARGIN + 5.6 * cm, MARGIN + 9.5 * cm]
c.setFont("Helvetica-Bold", 9)
for cx, h in zip(cols, ["Round", "Groups", "Zetas used", "Pairing distance"]):
    c.drawString(cx, y, h)
y -= 0.4 * cm
c.line(MARGIN + 0.4 * cm, y + 0.1 * cm, WIDTH - MARGIN, y + 0.1 * cm)
y -= 0.15 * cm
c.setFont("Helvetica", 9)
for r in [("1", "1", "1", "128 apart"), ("2", "2", "2", "64 apart"), ("3", "4", "4", "32 apart"),
          ("4", "8", "8", "16 apart"), ("5", "16", "16", "8 apart"), ("6", "32", "32", "4 apart"),
          ("7", "64", "64", "2 apart")]:
    for cx, val in zip(cols, r):
        c.drawString(cx, y, val)
    y -= 0.42 * cm

gap(0.2 * cm)
body("1+2+4+8+16+32+64 = 127, so every zeta gets used exactly once.")
gap(0.3 * cm)
body("The formula run on every single pair (a, b):")
mono("t     = zeta x b   mod q")
mono("new a = a + t      mod q")
mono("new b = a - t      mod q")
gap(0.2 * cm)
body("That is called a butterfly. It happens 128 times per round, 7 rounds, so 896 times")
body("in total for one polynomial.")

gap(0.5 * cm)
sub("c_hat_coefficient and c_hat_maker  -  the multiply")
body("WHAT: multiplies two transformed polynomials together.")
body("HOW: pairs here are NEIGHBOURS (position 0 with 1, 2 with 3...), not far apart like")
body("in hat_maker. Every pair gets its OWN gamma - no sharing.")
gap(0.25 * cm)
mono("c0 = (a0 x b0) + (a1 x b1 x gamma)   mod q")
mono("c1 = (a0 x b1) + (a1 x b0)           mod q")
gap(0.2 * cm)
body("c_hat_coefficient does one pair. c_hat_maker runs it across all 128 pairs.")

gap(0.5 * cm)
sub("NTT_final(c_hat)  -  the reverse transform")
body("WHAT: turns the transformed answer back into a normal polynomial.")
body("HOW: same 7 rounds but backwards - pairing goes 2, 4, 8 ... up to 128. Reads")
body("zeta_reverse forwards. The formula itself flips too:")
gap(0.25 * cm)
mono("new a = a + b                    mod q")
mono("new b = zeta_reverse x (b - a)   mod q")
gap(0.2 * cm)
body("Then one last step: every number gets multiplied by 3303. That cancels out a leftover")
body("factor that builds up from doing 7 rounds.")

gap(0.5 * cm)
sub("ntt_multiply(f, g)")
body("WHAT: bundles all of the above into one function.")
body("HOW: hat_maker(f), hat_maker(g), c_hat_maker, NTT_final. This is the ONLY one the")
body("rest of the code actually calls - it is a straight drop-in replacement for poly_mult.")

new_page()

# =================================================================
heading("Groups 4 and 5: Making Random Numbers")
body("Two completely different jobs here, using two different tools.")
gap(0.4 * cm)

sub("Group 4 - SMALL numbers, for secrets and noise (S, e, r, e_one, e_two)")
body("These need to be TINY - only -2 to +2 - because they are the noise that makes the")
body("lattice problem hard while still letting the message decode correctly.")
gap(0.3 * cm)
body("CBD_TABLE - 256 entries, one for every possible byte value. Each entry gives back")
body("2 small coefficients. Written out by hand rather than calculated.")
gap(0.2 * cm)
mono("byte 0   -> [ 0,  0]")
mono("byte 1   -> [ 1,  0]")
mono("byte 12  -> [-2,  0]")
mono("byte 255 -> [ 0,  0]")
gap(0.3 * cm)
body("poly_builder(poly_bytes, table)")
body("WHAT: turns a chunk of bytes into a full polynomial.")
body("HOW: looks up every byte in the table and glues the pairs together end to end.")
body("128 bytes in gives 256 coefficients out, which is exactly one polynomial.")

gap(0.6 * cm)
sub("Group 5 - BIG numbers, for the matrix A")
body("These need to be spread evenly across the whole 0 to 3328 range - the opposite of")
body("the small ones.")
gap(0.3 * cm)
body("poly_generator_from_seed(seed)")
body("WHAT: builds one cell of the matrix A from a seed.")
body("HOW, step by step:")
gap(0.2 * cm)
body("1. stretch the seed into 700 bytes using shake_128", indent=0.4 * cm)
body("2. read the stream 3 bytes at a time", indent=0.4 * cm)
body("3. each group of 3 bytes gives two 12-bit candidate numbers (d1 and d2)", indent=0.4 * cm)
body("4. keep any candidate under q, THROW AWAY anything 3329 or over", indent=0.4 * cm)
body("5. stop as soon as 256 coefficients have been kept", indent=0.4 * cm)
gap(0.3 * cm)
body("Step 4 is the important one - it is called rejection sampling. 12 bits can hold up to")
body("4095, but we only want up to 3328. Simply wrapping the extras round with % q would")
body("make the low numbers slightly more likely than the high ones. Throwing them away")
body("instead keeps everything perfectly even.")

new_page()

# =================================================================
heading("Group 6a: Byte Packing")
body("Hash functions only accept bytes, and real implementations have to agree byte for")
body("byte. Python's str() would not do - it writes numbers out as readable TEXT, which")
body("wastes space and is Python-specific.")
gap(0.4 * cm)

body("The number 1729 written two ways:")
gap(0.25 * cm)
mono('as text:  "1729"  =  4 characters  =  32 bits')
mono("as bits:  11011000001       =  12 bits")
gap(0.3 * cm)
body("Nearly 3x smaller, and completely unambiguous across any language.")

gap(0.5 * cm)
sub("bits_to_bytes and bytes_to_bits")
body("WHAT: convert between a list of individual bits and real bytes.")
body("HOW: peel bits off one at a time using % 2 (gives the bit) and // 2 (moves along).")
body("The same trick used in the CBD work early on.")

gap(0.5 * cm)
sub("byte_encode(F, d)")
body("WHAT: packs a list of numbers into tightly packed real bytes, d bits each.")
body("HOW: turn each number into d bits, glue every bit into one long list, pack into bytes.")
gap(0.3 * cm)
body("Different d values used in this project:")
mono("d = 12  ->  b and the raw polynomials  (256 x 12 = 384 bytes)")
mono("d = 11  ->  u after compression        (256 x 11 = 352 bytes)")
mono("d = 5   ->  v after compression        (256 x  5 = 160 bytes)")
mono("d = 1   ->  m, which is just bits      (256 x  1 =  32 bytes)")

gap(0.4 * cm)
sub("byte_decode(B, d)")
body("WHAT: the exact reverse - unpacks bytes back into a list of numbers.")
body("HOW: unpack to bits, read d bits at a time, rebuild each number.")

new_page()

# =================================================================
heading("Group 6b: Compression")
body("Compression deliberately throws accuracy away to save space. Unlike byte_encode,")
body("which is lossless, this one is lossy ON PURPOSE.")
gap(0.4 * cm)

sub("The idea - the same position on a shorter ruler")
gap(0.3 * cm)

# ruler diagram
ruler_y = y
c.setFont("Helvetica", 8)
c.drawString(MARGIN, ruler_y, "big range:")
c.line(MARGIN + 2.5 * cm, ruler_y + 3, MARGIN + 13 * cm, ruler_y + 3)
c.line(MARGIN + 2.5 * cm, ruler_y, MARGIN + 2.5 * cm, ruler_y + 6)
c.line(MARGIN + 13 * cm, ruler_y, MARGIN + 13 * cm, ruler_y + 6)
c.drawString(MARGIN + 2.4 * cm, ruler_y - 10, "0")
c.drawString(MARGIN + 12.7 * cm, ruler_y - 10, "3328")
mark = MARGIN + 2.5 * cm + (1000 / 3328) * 10.5 * cm
c.circle(mark, ruler_y + 3, 3, stroke=1, fill=1)
c.drawString(mark - 0.3 * cm, ruler_y + 10, "1000")

y -= 1.5 * cm
ruler_y = y
c.drawString(MARGIN, ruler_y, "small range:")
c.line(MARGIN + 2.5 * cm, ruler_y + 3, MARGIN + 13 * cm, ruler_y + 3)
c.line(MARGIN + 2.5 * cm, ruler_y, MARGIN + 2.5 * cm, ruler_y + 6)
c.line(MARGIN + 13 * cm, ruler_y, MARGIN + 13 * cm, ruler_y + 6)
c.drawString(MARGIN + 2.4 * cm, ruler_y - 10, "0")
c.drawString(MARGIN + 12.7 * cm, ruler_y - 10, "2047")
mark2 = MARGIN + 2.5 * cm + (615 / 2047) * 10.5 * cm
c.circle(mark2, ruler_y + 3, 3, stroke=1, fill=1)
c.drawString(mark2 - 0.25 * cm, ruler_y + 10, "615")

y -= 1.2 * cm
body("1000 sits about 30% along the big range. 30% along the small range is 615.")
body("Same position, shorter ruler. That is the entire idea.")
gap(0.3 * cm)
mono("(1000 / 3328) x 2047  =  615.08  ->  rounds to 615")

gap(0.5 * cm)
sub("The four functions")
body("compress_u / decompress_u   - always 11 bits (0 to 2047)")
body("compress_v / decompress_v   - always 5 bits  (0 to 31)")
gap(0.25 * cm)
body("HOW: the code does it with integer maths only, because FIPS 203 forbids floating")
body("point. The (a + b//2) // b pattern is just the integer way of rounding to nearest")
body("instead of always rounding down.")

gap(0.4 * cm)
sub("Why v gets squeezed 6x harder than u")
body("v only ever has to answer one rough question at the very end: closer to 0, or closer")
body("to halfway? Those two targets are miles apart, so even at 5 bits the answer is still")
body("obvious. Losing detail costs nothing.")
gap(0.2 * cm)
body("u is different - it feeds into real ongoing algebra (multiplied by S, subtracted from")
body("v). Sloppiness there would snowball and could push the FINAL answer into the wrong")
body("half, breaking the very decision v is trying to make. So u stays more precise.")
gap(0.3 * cm)
body("Measured error after a round trip:  u is off by at most 1,  v by at most 52.")

new_page()

# =================================================================
heading("Group 6c: Building the Real Ciphertext")
body("These two are what actually turn Alice's working numbers into something sendable.")
gap(0.4 * cm)

sub("ciphertext_maker(u, v)")
gap(0.3 * cm)

# ciphertext construction diagram
bw2, bh2 = 3.4 * cm, 1 * cm
t = y
box(MARGIN, t, bw2, bh2, "u", "4 polys, 12 bits")
box(MARGIN + 9 * cm, t, bw2, bh2, "v", "1 poly, 12 bits")
arrow(MARGIN + bw2 / 2, t - bh2, MARGIN + bw2 / 2, t - bh2 - 0.8 * cm, "compress 11")
arrow(MARGIN + 9 * cm + bw2 / 2, t - bh2, MARGIN + 9 * cm + bw2 / 2, t - bh2 - 0.8 * cm, "compress 5")

t2 = t - bh2 - 0.8 * cm
box(MARGIN, t2, bw2, bh2, "c1", "4 x 352 = 1408 bytes")
box(MARGIN + 9 * cm, t2, bw2, bh2, "c2", "160 bytes")

midx2 = (MARGIN + bw2 / 2 + MARGIN + 9 * cm + bw2 / 2) / 2
c.line(MARGIN + bw2 / 2, t2 - bh2 - 0.5 * cm, MARGIN + 9 * cm + bw2 / 2, t2 - bh2 - 0.5 * cm)
c.line(MARGIN + bw2 / 2, t2 - bh2, MARGIN + bw2 / 2, t2 - bh2 - 0.5 * cm)
c.line(MARGIN + 9 * cm + bw2 / 2, t2 - bh2, MARGIN + 9 * cm + bw2 / 2, t2 - bh2 - 0.5 * cm)
arrow(midx2, t2 - bh2 - 0.5 * cm, midx2, t2 - bh2 - 1.1 * cm)

t3 = t2 - bh2 - 1.1 * cm
box(midx2 - bw2 / 2, t3, bw2, bh2, "c", "1568 bytes")
y = t3 - bh2 - 0.8 * cm

gap(0.2 * cm)
body("1408 + 160 = 1568 bytes, which matches FIPS 203 Table 3 EXACTLY for ML-KEM-1024.")
body("This one blob is the only thing that travels from Alice to Bob.")

gap(0.5 * cm)
sub("ciphertext_opener(c)")
body("WHAT: exactly the reverse, run by Bob the moment he receives c.")
body("HOW: slice the first 1408 bytes off as u (in 352-byte chunks, one per poly), the")
body("remaining 160 as v. byte_decode each one, then decompress.")
gap(0.3 * cm)
body("IMPORTANT: what Bob gets back is CLOSE to Alice's original u and v but NOT identical.")
body("That is the lossy compression showing up, and it is completely expected. The message")
body("still decodes correctly, which is the whole point.")

c.save()
print("saved to", OUT_PATH)
