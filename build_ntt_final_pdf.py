import os

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

WIDTH, HEIGHT = A4
MARGIN = 2 * cm
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ntt_final_writeup.pdf")

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


def code_line(text, size=9.5, leading=12.5, indent=0.5 * cm):
    global y
    ensure_space(leading + 2)
    c.setFont("Courier", size)
    c.drawString(MARGIN + indent, y, text)
    y -= leading


def gap(amount=0.3 * cm):
    global y
    y -= amount


def draw_box(x, top_y, w, h, label, sub=""):
    c.roundRect(x, top_y - h, w, h, 5, stroke=1, fill=0)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(x + w / 2, top_y - h / 2 + (4 if sub else 0), label)
    if sub:
        c.setFont("Helvetica", 7.5)
        c.drawCentredString(x + w / 2, top_y - h / 2 - 8, sub)


def draw_arrow_down(x, top_y, length):
    c.line(x, top_y, x, top_y - length)
    c.line(x, top_y - length, x - 3, top_y - length + 6)
    c.line(x, top_y - length, x + 3, top_y - length + 6)


# =================================================================
heading("NTT Multiplication - Full Writeup")
body("Real Kyber scale: n=256, q=3329, zeta=17. Everything below is confirmed, hand-checked,")
body("and verified against the slow schoolbook method (MATCH: True).")

gap(0.5 * cm)
subheading("Part 1: The Maths")

gap(0.4 * cm)
subheading("The whole pipeline, as a diagram")
gap(0.3 * cm)

box_w, box_h = 3 * cm, 1.3 * cm
left_x = MARGIN
right_x = MARGIN + 8 * cm
top = y

draw_box(left_x, top, box_w, box_h, "f", "256 numbers")
draw_box(right_x, top, box_w, box_h, "g", "256 numbers")

draw_arrow_down(left_x + box_w / 2, top - box_h, 1 * cm)
draw_arrow_down(right_x + box_w / 2, top - box_h, 1 * cm)
c.setFont("Helvetica-Oblique", 8)
c.drawCentredString(left_x + box_w / 2 + 1.2*cm, top - box_h - 0.6*cm, "hat_maker")
c.drawCentredString(right_x + box_w / 2 + 1.2*cm, top - box_h - 0.6*cm, "hat_maker")

top2 = top - box_h - 1 * cm
draw_box(left_x, top2, box_w, box_h, "f_hat", "transformed")
draw_box(right_x, top2, box_w, box_h, "g_hat", "transformed")

mid_x = (left_x + box_w/2 + right_x + box_w/2) / 2
draw_arrow_down(left_x + box_w/2, top2 - box_h, 0.8*cm)
draw_arrow_down(right_x + box_w/2, top2 - box_h, 0.8*cm)
c.line(left_x + box_w/2, top2 - box_h - 0.8*cm, right_x + box_w/2, top2 - box_h - 0.8*cm)
draw_arrow_down(mid_x, top2 - box_h - 0.8*cm, 0.5*cm)
c.setFont("Helvetica-Oblique", 8)
c.drawCentredString(mid_x + 1.5*cm, top2 - box_h - 1*cm, "c_hat_maker")

top3 = top2 - box_h - 1.5 * cm
draw_box(mid_x - box_w/2, top3, box_w, box_h, "c_hat", "256 numbers")

draw_arrow_down(mid_x, top3 - box_h, 1*cm)
c.setFont("Helvetica-Oblique", 8)
c.drawCentredString(mid_x + 1.3*cm, top3 - box_h - 0.6*cm, "NTT_final")

top4 = top3 - box_h - 1.5 * cm
draw_box(mid_x - box_w/2, top4, box_w, box_h, "result", "f x g, done")

y = top4 - box_h - 1 * cm

new_page()

# =================================================================
subheading("The single formula used in hat_maker (forward)")
body("Take a pair (a, b) and this group's zeta:")
code_line("t = zeta * b mod q")
code_line("new a = (a + t) mod q")
code_line("new b = (a - t) mod q")

gap(0.5 * cm)
subheading("The 7 rounds of hat_maker")
gap(0.2 * cm)

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
body("1+2+4+8+16+32+64 = 127 - every zeta gets used exactly once. Position 0 always lands")
body("in the first group each round, so it happens to use indices 1, 2, 4, 8, 16, 32, 64.")

gap(0.5 * cm)
subheading("Real worked example - position 0, all 7 rounds of hat_maker")
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
    code_line(line)

new_page()

# =================================================================
subheading("The formula used in c_hat_maker (the multiply step)")
body("Pairs here are consecutive neighbours (position 0&1, 2&3, ...) - NOT far apart like")
body("hat_maker's pairs. Every single pair gets its own gamma (no sharing within a group).")
gap(0.2 * cm)
code_line("c0 = (a0 x b0) + (a1 x b1 x gamma)  mod q")
code_line("c1 = (a0 x b1) + (a1 x b0)          mod q")

gap(0.5 * cm)
subheading("Real worked example - pair 0 of c_hat_maker")
mult_steps = [
    "a0,a1 = 1507, 1456  (from f_hat)      b0,b1 = 194, 1315  (from g_hat)     gamma = 17",
    "",
    "step 1: a0 x b0 = 1507 x 194 = 292,358",
    "step 2: a1 x b1 = 1456 x 1315 = 1,914,640",
    "step 3: step2 x gamma = 1,914,640 x 17 = 32,548,880",
    "step 4: step1 + step3 = 292,358 + 32,548,880 = 32,841,238",
    "step 5: mod q -> c0 = 653",
    "",
    "step 6: a0 x b1 = 1507 x 1315 = 1,981,705",
    "step 7: a1 x b0 = 1456 x 194 = 282,464",
    "step 8: step6 + step7 = 1,981,705 + 282,464 = 2,264,169",
    "step 9: mod q -> c1 = 449",
]
for line in mult_steps:
    if line == "":
        gap(0.15 * cm)
    else:
        code_line(line)

gap(0.4 * cm)
body("Result for pair 0: (653, 449). This repeats for all 128 pairs, filling c_hat (256 numbers).")

new_page()

# =================================================================
subheading("The reverse process - NTT_final")
body("Same butterfly idea as hat_maker, but undone:")
body("- rounds go the OPPOSITE order: 2 apart, then 4, 8, 16, 32, 64, 128 apart")
body("- reads zeta_reverse forward (zeta flipped end to end) instead of zeta backward")
body("- the formula itself flips: add first, THEN multiply")
gap(0.2 * cm)
code_line("new a = (a + b) mod q")
code_line("new b = zeta_reverse_value x (b - a)  mod q")
gap(0.3 * cm)
body("One final step after all 7 reverse rounds: multiply every number in the list by 3303 -")
body("this cancels out a leftover scaling factor left behind by doing 7 rounds. After that,")
body("the list is the real, final answer to f x g.")

gap(0.6 * cm)
subheading("Part 2: The Code")
body("Everything above, as actual working Python, real names throughout:")

new_page()

# =================================================================
subheading("zeta, zeta_reverse, gamma - the lookup tables")
body("zeta: the 128 magic numbers straight from FIPS 203 Appendix A. Not calculated -")
body("just given to us, same idea as CBD_TABLE was.")
gap(0.15*cm)
body("zeta_reverse: literally zeta flipped end to end, so NTT_final can walk forward")
body("through it instead of walking zeta backwards.")
gap(0.15*cm)
body("gamma: a SEPARATE table of 128 numbers, also from Appendix A, used only in")
body("c_hat_maker, one per pair.")

gap(0.5 * cm)
subheading("hat_maker(f) - turns a normal poly into its transformed shape")
code_line("def hat_maker(f):")
code_line("    f_hat = f.copy()")
code_line("    i = 1")
code_line("    length = 128")
code_line("    while length >= 2:")
code_line("        start = 0")
code_line("        while start < n:")
code_line("            z = zeta[i]")
code_line("            i += 1")
code_line("            for j in range(start, start + length):")
code_line("                t = (z * f_hat[j + length]) % q")
code_line("                f_hat[j + length] = (f_hat[j] - t) % q")
code_line("                f_hat[j] = (f_hat[j] + t) % q")
code_line("            start += 2 * length")
code_line("        length //= 2")
code_line("    return f_hat")

new_page()

# =================================================================
subheading("c_hat_coefficient and c_hat_maker - the multiply step")
code_line("def c_hat_coefficient(a0, a1, b0, b1, gamma_value):")
code_line("    c0 = (a0 * b0 + a1 * b1 * gamma_value) % q")
code_line("    c1 = (a0 * b1 + a1 * b0) % q")
code_line("    return c0, c1")
gap(0.3*cm)
code_line("def c_hat_maker(f_hat, g_hat):")
code_line("    c_hat = [0] * n")
code_line("    for i in range(128):")
code_line("        c0, c1 = c_hat_coefficient(")
code_line("            f_hat[2*i], f_hat[2*i+1],")
code_line("            g_hat[2*i], g_hat[2*i+1], gamma[i])")
code_line("        c_hat[2*i] = c0")
code_line("        c_hat[2*i+1] = c1")
code_line("    return c_hat")

gap(0.6 * cm)
subheading("NTT_final(c_hat) - turns c_hat back into the real answer")
code_line("def NTT_final(c_hat):")
code_line("    f = c_hat.copy()")
code_line("    i = 0")
code_line("    length = 2")
code_line("    while length <= 128:")
code_line("        start = 0")
code_line("        while start < n:")
code_line("            z = zeta_reverse[i]")
code_line("            i += 1")
code_line("            for j in range(start, start + length):")
code_line("                t = f[j]")
code_line("                f[j] = (t + f[j + length]) % q")
code_line("                f[j + length] = (z * (f[j + length] - t)) % q")
code_line("            start += 2 * length")
code_line("        length *= 2")
code_line("    f = [(x * 3303) % q for x in f]")
code_line("    return f")

new_page()

# =================================================================
subheading("Naming reference")
gap(0.2*cm)
name_rows = [
    ("Old name", "New name"),
    ("zetas", "zeta"),
    ("(new)", "zeta_reverse"),
    ("zetas_mult", "gamma"),
    ("NTT(f)", "hat_maker"),
    ("NTT_inverse", "NTT_final"),
    ("base_case_multiply", "c_hat_coefficient"),
    ("multiply_ntts", "c_hat_maker"),
    ("poly_mult_schoolbook", "unchanged - unrelated to NTT itself"),
]
c.setFont("Helvetica-Bold", 10)
c.drawString(MARGIN, y, name_rows[0][0])
c.drawString(MARGIN + 6*cm, y, name_rows[0][1])
y -= 0.5*cm
c.line(MARGIN, y+0.15*cm, WIDTH-MARGIN, y+0.15*cm)
y -= 0.15*cm
c.setFont("Helvetica", 10)
for old, new in name_rows[1:]:
    c.drawString(MARGIN, y, old)
    c.drawString(MARGIN + 6*cm, y, new)
    y -= 0.55*cm

gap(0.6*cm)
subheading("Final check")
body("f (first 5):        [2619, 456, 102, 3037, 1126]")
body("g (first 5):        [262, 1384, 86, 2409, 2268]")
body("f_hat (first 5):    [1507, 1456, 1833, 934, 1178]")
body("g_hat (first 5):    [194, 1315, 2820, 3001, 1536]")
body("c_hat (first 5):    [653, 449, 551, 1966, 576]")
body("schoolbook result:  [1331, 2055, 1467, 538, 3010]")
body("NTT result:         [1331, 2055, 1467, 538, 3010]")
gap(0.2*cm)
body("MATCH: True", size=13)

c.save()
print("saved to", OUT_PATH)
