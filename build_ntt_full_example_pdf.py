import os

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

WIDTH, HEIGHT = A4
MARGIN = 2 * cm
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ntt_full_multiplication_example.pdf")

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
heading("Multiplying Two Polynomials with NTT - Full Worked Example")
body("This document does one complete polynomial multiplication using the NTT method,")
body("done entirely by hand-style arithmetic, following the exact same structure as FIPS 203's")
body("real algorithms (Algorithm 9-12), just shrunk down to n=8 instead of n=256 so every")
body("number can be seen and checked by hand.")
gap(0.5 * cm)
body("Sizes used for this example: n=8, q=17, zeta=9 (instead of the real n=256, q=3329,")
body("zeta=17). zeta=9 was chosen because it has the same special property real Kyber's")
body("zeta needs: zeta^4 = -1 (mod 17), same as zeta^128 = -1 (mod 3329) in the real thing.")

gap(0.6 * cm)
subheading("What we are multiplying")
body("f(x) = 1 + 2x + 0x^2 + 1x^3 + 0x^4 + 0x^5 + 1x^6 + 0x^7   ->   as a list: 1, 2, 0, 1, 0, 0, 1, 0")
body("g(x) = 2 + 0x + 1x^2 + 0x^3 + 1x^4 + 0x^5 + 0x^6 + 1x^7   ->   as a list: 2, 0, 1, 0, 1, 0, 0, 1")
gap(0.3 * cm)
body("The goal: compute f(x) times g(x), reduced mod (x^8 + 1) and mod 17 - and get the exact")
body("same answer whether we do it the slow schoolbook way or the fast NTT way.")

gap(0.6 * cm)
subheading("Why we transform f and g at all")
body("Multiplying two 8-coefficient polynomials the normal (schoolbook) way means checking")
body("every pair of terms against each other - a real amount of work. NTT rearranges each")
body("polynomial's numbers into a different list first; once both lists are rearranged this way,")
body("multiplying them together becomes simple - just matching pairs straight across.")

new_page()

# ---------------------------------------------------------------
heading("Step 1: Transform f (NTT)")
body("We take numbers two at a time and combine them with one multiply, then one add and")
body("one subtract - this is the 'butterfly' step. There are two rounds; round 2 splits into two")
body("smaller groups, each using a different magic number.")
gap(0.4 * cm)

subheading("Round 1 - magic number 13")
f1_lines = [
    ("Pair (position 0, position 4): values 1, 0", ["13 x 0 = 0", "1 + 0 = 1  ->  position 0", "1 - 0 = 1  ->  position 4"]),
    ("Pair (position 1, position 5): values 2, 0", ["13 x 0 = 0", "2 + 0 = 2  ->  position 1", "2 - 0 = 2  ->  position 5"]),
    ("Pair (position 2, position 6): values 0, 1", ["13 x 1 = 13", "0 + 13 = 13  ->  position 2", "0 - 13 = -13 -> 4 (mod 17)  ->  position 6"]),
    ("Pair (position 3, position 7): values 1, 0", ["13 x 0 = 0", "1 + 0 = 1  ->  position 3", "1 - 0 = 1  ->  position 7"]),
]
for title, steps in f1_lines:
    body(title)
    for s in steps:
        body(s, indent=0.5 * cm)
    gap(0.2 * cm)

body("List after Round 1:  1, 2, 13, 1, 1, 2, 4, 1", size=11)
gap(0.4 * cm)

subheading("Round 2, Group A - magic number 9 (positions 0-3)")
f2a_lines = [
    ("Pair (position 0, position 2): values 1, 13", ["9 x 13 = 117 -> 15 (mod 17)", "1 + 15 = 16  ->  position 0", "1 - 15 = -14 -> 3 (mod 17)  ->  position 2"]),
    ("Pair (position 1, position 3): values 2, 1", ["9 x 1 = 9", "2 + 9 = 11  ->  position 1", "2 - 9 = -7 -> 10 (mod 17)  ->  position 3"]),
]
for title, steps in f2a_lines:
    body(title)
    for s in steps:
        body(s, indent=0.5 * cm)
    gap(0.2 * cm)

subheading("Round 2, Group B - magic number 15 (positions 4-7)")
f2b_lines = [
    ("Pair (position 4, position 6): values 1, 4", ["15 x 4 = 60 -> 9 (mod 17)", "1 + 9 = 10  ->  position 4", "1 - 9 = -8 -> 9 (mod 17)  ->  position 6"]),
    ("Pair (position 5, position 7): values 2, 1", ["15 x 1 = 15", "2 + 15 = 17 -> 0 (mod 17)  ->  position 5", "2 - 15 = -13 -> 4 (mod 17)  ->  position 7"]),
]
for title, steps in f2b_lines:
    body(title)
    for s in steps:
        body(s, indent=0.5 * cm)
    gap(0.2 * cm)

body("Final transformed f (called f_hat):  16, 11, 3, 10, 10, 0, 9, 4", size=11)

new_page()

# ---------------------------------------------------------------
heading("Step 2: Transform g (NTT)")
body("Exact same process as Step 1, run on g instead of f.")
gap(0.4 * cm)

g_pairs = [
    ("Round 1, magic number 13", [
        ("Pair (position 0, position 4): values 2, 1", ["13 x 1 = 13", "2 + 13 = 15  ->  position 0", "2 - 13 = -11 -> 6 (mod 17)  ->  position 4"]),
        ("Pair (position 1, position 5): values 0, 0", ["13 x 0 = 0", "0 + 0 = 0  ->  position 1", "0 - 0 = 0  ->  position 5"]),
        ("Pair (position 2, position 6): values 1, 0", ["13 x 0 = 0", "1 + 0 = 1  ->  position 2", "1 - 0 = 1  ->  position 6"]),
        ("Pair (position 3, position 7): values 0, 1", ["13 x 1 = 13", "0 + 13 = 13  ->  position 3", "0 - 13 = -13 -> 4 (mod 17)  ->  position 7"]),
    ]),
    ("Round 2, Group A - magic number 9 (positions 0-3, using Round 1 results)", [
        ("Pair (position 0, position 2): values 15, 1", ["9 x 1 = 9", "15 + 9 = 24 -> 7 (mod 17)  ->  position 0", "15 - 9 = 6  ->  position 2"]),
        ("Pair (position 1, position 3): values 0, 13", ["9 x 13 = 117 -> 15 (mod 17)", "0 + 15 = 15  ->  position 1", "0 - 15 = -15 -> 2 (mod 17)  ->  position 3"]),
    ]),
    ("Round 2, Group B - magic number 15 (positions 4-7)", [
        ("Pair (position 4, position 6): values 6, 1", ["15 x 1 = 15", "6 + 15 = 21 -> 4 (mod 17)  ->  position 4", "6 - 15 = -9 -> 8 (mod 17)  ->  position 6"]),
        ("Pair (position 5, position 7): values 0, 4", ["15 x 4 = 60 -> 9 (mod 17)", "0 + 9 = 9  ->  position 5", "0 - 9 = -9 -> 8 (mod 17)  ->  position 7"]),
    ]),
]
for round_title, pairs in g_pairs:
    subheading(round_title)
    for title, steps in pairs:
        body(title)
        for s in steps:
            body(s, indent=0.5 * cm)
        gap(0.2 * cm)
    gap(0.2 * cm)

body("Final transformed g (called g_hat):  7, 15, 6, 2, 4, 9, 8, 8", size=11)

new_page()

# ---------------------------------------------------------------
heading("Step 3: Multiply the transformed lists")
body("f_hat and g_hat get multiplied 2 numbers at a time (4 pairs total, since we have 8 numbers).")
body("Each pair also needs its own magic number (called gamma here): 9, 8, 15, 2 for pairs 1-4.")
body("The formula for each pair (a0,a1) from f_hat and (b0,b1) from g_hat:")
gap(0.2 * cm)
body("c0 = (a0 x b0) + (a1 x b1 x gamma)      c1 = (a0 x b1) + (a1 x b0)", indent=0.5*cm)
gap(0.4 * cm)

mult_pairs = [
    ("Pair 1: f_hat=(16,11), g_hat=(7,15), gamma=9", [
        "c0 = (16x7) + (11x15x9) = 112 + 1485",
        "112 mod 17 = 10,   1485 mod 17: 11x15=165, 165 mod 17=12, 12x9=108, 108 mod 17=6",
        "c0 = 10 + 6 = 16",
        "c1 = (16x15) + (11x7) = 240 + 77",
        "240 mod 17 = 2,   77 mod 17 = 9",
        "c1 = 2 + 9 = 11",
        "result: 16, 11",
    ]),
    ("Pair 2: f_hat=(3,10), g_hat=(6,2), gamma=8", [
        "c0 = (3x6) + (10x2x8) = 18 + 160",
        "18 mod 17 = 1,   160 mod 17 = 7",
        "c0 = 1 + 7 = 8",
        "c1 = (3x2) + (10x6) = 6 + 60",
        "60 mod 17 = 9",
        "c1 = 6 + 9 = 15",
        "result: 8, 15",
    ]),
    ("Pair 3: f_hat=(10,0), g_hat=(4,9), gamma=15", [
        "c0 = (10x4) + (0x9x15) = 40 + 0 = 40 -> 6 (mod 17)",
        "c1 = (10x9) + (0x4) = 90 + 0 = 90 -> 5 (mod 17)",
        "result: 6, 5",
    ]),
    ("Pair 4: f_hat=(9,4), g_hat=(8,8), gamma=2", [
        "c0 = (9x8) + (4x8x2) = 72 + 64",
        "72 mod 17 = 4,   64 mod 17 = 13",
        "c0 = 4 + 13 = 17 -> 0 (mod 17)",
        "c1 = (9x8) + (4x8) = 72 + 32",
        "72 mod 17 = 4,   32 mod 17 = 15",
        "c1 = 4 + 15 = 19 -> 2 (mod 17)",
        "result: 0, 2",
    ]),
]
for title, steps in mult_pairs:
    subheading(title)
    for s in steps:
        body(s, indent=0.5 * cm)
    gap(0.2 * cm)

body("Combined result (called h_hat):  16, 11, 8, 15, 6, 5, 0, 2", size=11)

new_page()

# ---------------------------------------------------------------
heading("Step 4: Transform back (inverse NTT)")
body("h_hat is still in the 'transformed' shape - not real coefficients yet. This step undoes")
body("the transform from Steps 1/2, run backwards, using the same magic numbers in reverse")
body("order, then one final scaling step at the end.")
gap(0.4 * cm)

inv_pairs = [
    ("Round 1 (reverse), magic number 15 (positions 0-3)", [
        ("Pair (position 0, position 2): values 16, 8", ["16 + 8 = 24 -> 7 (mod 17)  ->  position 0", "15 x (8-16) = 15 x -8 = -120 -> 16 (mod 17)  ->  position 2"]),
        ("Pair (position 1, position 3): values 11, 15", ["11 + 15 = 26 -> 9 (mod 17)  ->  position 1", "15 x (15-11) = 15 x 4 = 60 -> 9 (mod 17)  ->  position 3"]),
    ]),
    ("Round 1 (reverse), magic number 9 (positions 4-7)", [
        ("Pair (position 4, position 6): values 6, 0", ["6 + 0 = 6  ->  position 4", "9 x (0-6) = 9 x -6 = -54 -> 14 (mod 17)  ->  position 6"]),
        ("Pair (position 5, position 7): values 5, 2", ["5 + 2 = 7  ->  position 5", "9 x (2-5) = 9 x -3 = -27 -> 7 (mod 17)  ->  position 7"]),
    ]),
    ("Round 2 (reverse), magic number 13 - all 4 pairs, spanning the whole list", [
        ("Pair (position 0, position 4): values 7, 6", ["7 + 6 = 13  ->  position 0", "13 x (6-7) = 13 x -1 = -13 -> 4 (mod 17)  ->  position 4"]),
        ("Pair (position 1, position 5): values 9, 7", ["9 + 7 = 16  ->  position 1", "13 x (7-9) = 13 x -2 = -26 -> 8 (mod 17)  ->  position 5"]),
        ("Pair (position 2, position 6): values 16, 14", ["16 + 14 = 30 -> 13 (mod 17)  ->  position 2", "13 x (14-16) = 13 x -2 = -26 -> 8 (mod 17)  ->  position 6"]),
        ("Pair (position 3, position 7): values 9, 7", ["9 + 7 = 16  ->  position 3", "13 x (7-9) = 13 x -2 = -26 -> 8 (mod 17)  ->  position 7"]),
    ]),
]
for round_title, pairs in inv_pairs:
    subheading(round_title)
    for title, steps in pairs:
        body(title)
        for s in steps:
            body(s, indent=0.5 * cm)
        gap(0.2 * cm)
    gap(0.2 * cm)

body("List before the final step:  13, 16, 13, 16, 4, 8, 8, 8", size=11)
gap(0.3 * cm)
subheading("Final scaling step")
body("Multiply every single number in the list by 13 (this undoes a leftover factor of 4 from")
body("the transform - 4 x 13 = 52, and 52 mod 17 = 1, so 13 is chosen specifically to cancel it out).")
gap(0.2*cm)
body("13x13=169->16   16x13=208->4   13x13=169->16   16x13=208->4", indent=0.5*cm)
body("4x13=52->1   8x13=104->2   8x13=104->2   8x13=104->2", indent=0.5*cm)
gap(0.3 * cm)
body("Final result:  16, 4, 16, 4, 1, 2, 2, 2", size=12)

new_page()

# ---------------------------------------------------------------
heading("Step 5: Check against the slow schoolbook method")
body("Multiplying f and g the normal (schoolbook) way, reduced mod (x^8+1) and mod 17,")
body("gives the same list:")
gap(0.3 * cm)
body("Schoolbook result:  16, 4, 16, 4, 1, 2, 2, 2", size=12)
body("NTT result:          16, 4, 16, 4, 1, 2, 2, 2", size=12)
gap(0.3 * cm)
body("MATCH - both methods give the exact same answer.", size=12)

gap(0.6 * cm)
subheading("How this maps onto real FIPS 203 / Kyber")
body("Everything above follows the exact same structure as FIPS 203's real algorithms:")
body("Step 1/2 = Algorithm 9 (NTT). Step 3 = Algorithms 11/12 (MultiplyNTTs, BaseCaseMultiply).")
body("Step 4 = Algorithm 10 (NTT-1). The only difference at real Kyber scale (n=256, q=3329,")
body("zeta=17) is more numbers and more rounds (8 rounds instead of 2) - the actual arithmetic")
body("being done at each step is identical to what's shown here.")

c.save()
print("saved to", OUT_PATH)
