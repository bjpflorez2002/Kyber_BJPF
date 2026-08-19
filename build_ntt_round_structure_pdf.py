import os

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

WIDTH, HEIGHT = A4
MARGIN = 2 * cm
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ntt_round_structure.pdf")

c = canvas.Canvas(OUT_PATH, pagesize=A4)
y = HEIGHT - MARGIN


def heading(text, size=16):
    global y
    c.setFont("Helvetica-Bold", size)
    c.drawString(MARGIN, y, text)
    y -= 0.9 * cm


def subheading(text):
    global y
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGIN, y, text)
    y -= 0.65 * cm


def body(text, size=10.5, leading=14, indent=0):
    global y
    c.setFont("Helvetica", size)
    c.drawString(MARGIN + indent, y, text)
    y -= leading


def gap(amount=0.3 * cm):
    global y
    y -= amount


heading("How NTT Works - Confirmed Understanding")
body("This document is the algorithm structure as worked out and confirmed step by step:")
body("256 coefficients in the polynomial, 128 zeta numbers in the list, 7 rounds total.")

gap(0.5 * cm)
subheading("The one formula, used every single time")
body("Take a pair of numbers (a, b) and the round's zeta:")
body("new pair = (a + zeta x b,  a - zeta x b)   mod q", indent=0.5 * cm, size=12)

gap(0.6 * cm)
subheading("How the zeta list gets used")
body("There is ONE shared list of 128 zetas. There is ONE counter that starts at 1 and goes")
body("up by 1 every time ANY group, in any round, starts. Every group just grabs the next")
body("unused zeta from this single list - nothing is calculated, just read off in order.")

gap(0.6 * cm)
subheading("The 7 rounds")
gap(0.2 * cm)

table_y_start = y
col_positions = [MARGIN, MARGIN + 2.2*cm, MARGIN + 4.5*cm, MARGIN + 8*cm]
headers = ["Round", "Groups", "Zetas used", "Pairing distance"]
c.setFont("Helvetica-Bold", 10)
for cx, h in zip(col_positions, headers):
    c.drawString(cx, y, h)
y -= 0.5 * cm
c.line(MARGIN, y + 0.15*cm, WIDTH - MARGIN, y + 0.15*cm)
y -= 0.15 * cm

rows = [
    ("1", "1", "1 (index 1)", "128 apart"),
    ("2", "2", "2 (indices 2-3)", "64 apart"),
    ("3", "4", "4 (indices 4-7)", "32 apart"),
    ("4", "8", "8 (indices 8-15)", "16 apart"),
    ("5", "16", "16 (indices 16-31)", "8 apart"),
    ("6", "32", "32 (indices 32-63)", "4 apart"),
    ("7", "64", "64 (indices 64-127)", "2 apart"),
]
c.setFont("Helvetica", 10)
for row in rows:
    for cx, val in zip(col_positions, row):
        c.drawString(cx, y, val)
    y -= 0.55 * cm

gap(0.3 * cm)
body("1 + 2 + 4 + 8 + 16 + 32 + 64 = 127 - every single zeta in the list gets used exactly once.")

gap(0.6 * cm)
subheading("A real worked example - position 0, all 7 rounds")
examples = [
    "Round 1: (2619, 2044), zeta=1729  ->  becomes 1297",
    "Round 2: (1297, 1532), zeta=2580  ->  becomes 2334",
    "Round 3: (2334, 366),  zeta=2642  ->  becomes 567",
    "Round 4: (567, 1293),  zeta=1062  ->  becomes 2185",
    "Round 5: (2185, 3293), zeta=296   ->  becomes 1516",
    "Round 6: (1516, 3007), zeta=289   ->  becomes 1670",
    "Round 7: (1670, 1557), zeta=17    ->  becomes 1507",
]
for line in examples:
    body(line, indent=0.5 * cm)

gap(0.6 * cm)
subheading("Important: this is the WHOLE NTT transform, but only ONE part of a multiplication")
body("Everything above (all 7 rounds) is the complete NTT(f) function on its own - not a")
body("partial piece. To actually multiply two polynomials, this same 7-round process runs")
body("TWICE (once on f, once on g), then a separate multiply step combines them (using a")
body("different table, zetas_mult, pair by pair), then a reversed version of this same")
body("7-round process converts the result back into a normal polynomial.")

c.save()
print("saved to", OUT_PATH)
