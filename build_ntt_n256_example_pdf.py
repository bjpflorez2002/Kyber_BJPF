import os

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

WIDTH, HEIGHT = A4
MARGIN = 2 * cm
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ntt_n256_example.pdf")

c = canvas.Canvas(OUT_PATH, pagesize=A4)
y = HEIGHT - MARGIN


def new_page():
    global y
    c.showPage()
    y = HEIGHT - MARGIN


def ensure_space(needed):
    global y
    if y - needed < MARGIN:
        new_page()


def heading(text, size=16):
    global y
    ensure_space(1.2 * cm)
    c.setFont("Helvetica-Bold", size)
    c.drawString(MARGIN, y, text)
    y -= 0.9 * cm


def subheading(text):
    global y
    ensure_space(0.9 * cm)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGIN, y, text)
    y -= 0.65 * cm


def body(text, size=10.5, leading=14, indent=0):
    global y
    ensure_space(leading + 2)
    c.setFont("Helvetica", size)
    c.drawString(MARGIN + indent, y, text)
    y -= leading


def gap(amount=0.3 * cm):
    global y
    y -= amount


# ---------------------------------------------------------------
heading("NTT at Real Scale: n = 256")
body("The n=8 example showed the full process, every single step, because it was small enough")
body("to fit on a page. At real Kyber size (n=256, q=3329, zeta=17), the SAME exact process")
body("happens - just far more of it. This document shows the scale, the real magic numbers,")
body("and a real excerpt of the very first few steps - not the whole thing, since a complete")
body("trace would be roughly 1,024 individual butterflies long.")

gap(0.6 * cm)
subheading("The scale, compared to the small example")
body("n=8 example:  2 rounds,  6 butterflies total")
body("n=256 real:   8 rounds,  1,024 butterflies total  (8 rounds x 128 per round)")
gap(0.3 * cm)
body("Same idea, same mechanism (one multiply, then add/subtract) - just repeated far more")
body("times, since there are 256 numbers to process instead of 8.")

gap(0.6 * cm)
subheading("The real magic number chain (starting from zeta=17, mod 3329)")
body("Same rule as before: start with 17, keep multiplying by 17 and reducing mod 3329.")
gap(0.2 * cm)
chain = [1729, 2580, 3289, 2642, 630, 1897, 848, 1062]
for idx, val in enumerate(chain, start=1):
    body(f"link {idx}:  {val}", indent=0.5 * cm)
body("... this chain continues for 127 links total (n/2 - 1 = 127), same idea throughout.")

new_page()

# ---------------------------------------------------------------
heading("A real excerpt: the first 3 butterflies of Round 1")
body("Example polynomial (only a few non-zero coefficients shown, rest are 0 for readability):")
body("position 0 = 5,  position 1 = 12,  position 2 = 300")
body("position 128 = 40,  position 129 = 900,  position 130 = 3")
gap(0.3 * cm)
body("Round 1 pairs position j with position j+128 (same shape as the n=8 example pairing")
body("j with j+4 - just a bigger jump, since n/2=128 here instead of n/2=4).")
gap(0.3 * cm)
body("Magic number for Round 1: 1729", size=11)

gap(0.4 * cm)

excerpt = [
    ("Pair (position 0, position 128): values 5, 40", [
        "t = 1729 x 40 mod 3329 = 2580",
        "5 + 2580 mod 3329 = 2585   ->  position 0",
        "5 - 2580 mod 3329 = 754    ->  position 128",
    ]),
    ("Pair (position 1, position 129): values 12, 900", [
        "t = 1729 x 900 mod 3329 = 1457",
        "12 + 1457 mod 3329 = 1469   ->  position 1",
        "12 - 1457 mod 3329 = 1884   ->  position 129",
    ]),
    ("Pair (position 2, position 130): values 300, 3", [
        "t = 1729 x 3 mod 3329 = 1858",
        "300 + 1858 mod 3329 = 2158   ->  position 2",
        "300 - 1858 mod 3329 = 1771   ->  position 130",
    ]),
]
for title, steps in excerpt:
    subheading(title)
    for s in steps:
        body(s, indent=0.5 * cm)
    gap(0.2 * cm)

body("This exact process (one multiply, one add, one subtract) repeats for the remaining 125")
body("pairs of Round 1, then again for all of Rounds 2 through 8 - same mechanism, just a lot")
body("more of it. Not shown in full here since it would just be the same arithmetic pattern")
body("copied roughly 1,020 more times.")

new_page()

# ---------------------------------------------------------------
heading("Confirming it all still works at real scale")
body("Running the complete real n=256 pipeline (NTT.NTT_Multiplication.py) - transforming two")
body("full 256-coefficient polynomials, multiplying them the fast way, transforming back, and")
body("comparing to the slow schoolbook answer:")
gap(0.3 * cm)
body("schoolbook and NTT results match: True", size=12)
gap(0.2 * cm)
body("first 5 coefficients, schoolbook:  [2720, 381, 397, 2480, 2871]", indent=0.5*cm)
body("first 5 coefficients, NTT method:  [2720, 381, 397, 2480, 2871]", indent=0.5*cm)

gap(0.6 * cm)
subheading("Summary")
body("Real Kyber's NTT is exactly the n=8 process you already worked through by hand - the")
body("same butterfly mechanism, the same idea of a magic-number chain built from one starting")
body("value - just scaled up to 256 numbers and 8 rounds instead of 8 numbers and 2 rounds.")
body("Nothing new happens conceptually between the small example and the real thing; there is")
body("simply far more of the same arithmetic repeated.")

c.save()
print("saved to", OUT_PATH)
