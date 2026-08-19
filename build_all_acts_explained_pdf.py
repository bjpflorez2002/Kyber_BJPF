import os

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

WIDTH, HEIGHT = A4
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "all_acts_explained.pdf")

c = canvas.Canvas(OUT_PATH, pagesize=A4)


def draw_title(text):
    c.setFont("Helvetica-Bold", 20)
    c.drawString(2 * cm, HEIGHT - 2.2 * cm, text)
    c.line(2 * cm, HEIGHT - 2.5 * cm, WIDTH - 2 * cm, HEIGHT - 2.5 * cm)


def draw_box(x, y, w, h, label, sublabel=""):
    c.roundRect(x, y, w, h, 6, stroke=1, fill=0)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(x + w / 2, y + h / 2 + (4 if sublabel else 0), label)
    if sublabel:
        c.setFont("Helvetica", 9)
        c.drawCentredString(x + w / 2, y + h / 2 - 10, sublabel)


def draw_arrow(x1, y1, x2, y2, label=""):
    c.line(x1, y1, x2, y2)
    # simple arrowhead
    import math
    angle = math.atan2(y2 - y1, x2 - x1)
    ah = 6
    c.line(x2, y2, x2 - ah * math.cos(angle - 0.4), y2 - ah * math.sin(angle - 0.4))
    c.line(x2, y2, x2 - ah * math.cos(angle + 0.4), y2 - ah * math.sin(angle + 0.4))
    if label:
        c.setFont("Helvetica-Oblique", 8)
        c.drawCentredString((x1 + x2) / 2, (y1 + y2) / 2 + 6, label)


def draw_paragraph(x, y, width, lines, font="Helvetica", size=11, leading=15):
    c.setFont(font, size)
    cursor_y = y
    for line in lines:
        c.drawString(x, cursor_y, line)
        cursor_y -= leading
    return cursor_y


# ---------------------------------------------------------------
# Page 1: Act 1 - Bob / KeyGen
# ---------------------------------------------------------------
draw_title("Act 1: Bob's KeyGen")

top = HEIGHT - 4.5 * cm
box_w, box_h = 3.6 * cm, 1.6 * cm

draw_box(2 * cm, top, box_w, box_h, "rho", "random seed")
draw_arrow(2 * cm + box_w, top + box_h / 2, 7 * cm, top + box_h / 2, "expand")
draw_box(7 * cm, top, box_w, box_h, "A", "the matrix")

draw_box(2 * cm, top - 3 * cm, box_w, box_h, "sigma", "random seed")
draw_arrow(2 * cm + box_w, top - 3 * cm + box_h / 2, 7 * cm, top - 3 * cm + box_h / 2, "CBD table")
draw_box(7 * cm, top - 3 * cm, box_w, box_h, "S, e", "small secret + noise")

draw_arrow(7 * cm + box_w / 2, top, 7 * cm + box_w / 2, top - 3 * cm + box_h, "")
draw_arrow(7 * cm + box_w, top - 1.5 * cm, 12.5 * cm, top - 1.5 * cm, "combine")
draw_box(12.5 * cm, top - 1.5 * cm, box_w, box_h, "b", "A.S + e")

draw_arrow(2 * cm + box_w / 2, top - 3 * cm, 2 * cm + box_w / 2, top - 4.5 * cm, "")
draw_box(2 * cm, top - 6 * cm, box_w, box_h, "(rho, b)", "public key")
draw_arrow(2 * cm + box_w, top - 6 * cm + box_h / 2, 7 * cm, top - 6 * cm + box_h / 2, "hash once")
draw_box(7 * cm, top - 6 * cm, box_w, box_h, "H(ek)", "saved for later")

text_y = top - 8.5 * cm
lines = [
    "Bob makes a small random seed (rho) and expands it into the full matrix A -",
    "he never has to send the whole matrix, just this one small seed.",
    "",
    "A second seed (sigma) gets tagged with a different position for each",
    "polynomial and turned into small values via the CBD table - this gives",
    "S (Bob's private secret) and e (noise).",
    "",
    "b = A.S + e is computed with normal poly_add/poly_mult.",
    "",
    "Bob's public key is just (rho, b) - never the whole matrix. He also",
    "hashes his own public key once, right now, and saves the result (H(ek))",
    "so he never has to redo that specific hash later.",
]
draw_paragraph(2 * cm, text_y, WIDTH - 4 * cm, lines)
c.showPage()

# ---------------------------------------------------------------
# Page 2: Act 2 - Alice / Encapsulate
# ---------------------------------------------------------------
draw_title("Act 2: Alice's Encapsulate")

top = HEIGHT - 4.5 * cm
draw_box(2 * cm, top, box_w, box_h, "rho, b", "received")
draw_arrow(2 * cm + box_w, top + box_h / 2, 7 * cm, top + box_h / 2, "rebuild")
draw_box(7 * cm, top, box_w, box_h, "Alice_A", "matches Bob's A")

draw_box(2 * cm, top - 2.5 * cm, box_w, box_h, "m", "Alice's message")
draw_arrow(2 * cm + box_w, top - 2.5 * cm + box_h / 2, 7 * cm, top - 2.5 * cm + box_h / 2, "hash + split")
draw_box(7 * cm, top - 2.5 * cm, box_w, box_h, "K, r_coins", "sha3_512 halves")

draw_arrow(7 * cm + box_w / 2, top - 2.5 * cm, 7 * cm + box_w / 2, top - 4 * cm, "position tags")
draw_box(7 * cm, top - 5.5 * cm, box_w, box_h, "r, e_one, e_two", "CBD table")

draw_arrow(7 * cm + box_w, top - 5.5 * cm + box_h / 2, 12.5 * cm, top - 5.5 * cm + box_h / 2, "combine")
draw_box(12.5 * cm, top - 5.5 * cm, box_w, box_h, "u, v", "sent to Bob")

text_y = top - 8 * cm
lines = [
    "Alice rebuilds A herself from the rho she received - same expansion",
    "Bob used. She also computes H(ek) herself, from (rho, b).",
    "",
    "Alice picks her message m (real randomness, via secrets). She hashes",
    "(m + H(ek)) with sha3_512, getting 64 bytes back, and splits that in",
    "half: the first half becomes K (the real shared secret, saved for",
    "later), the second half becomes r_coins.",
    "",
    "r_coins gets tagged with a position for each polynomial needed and",
    "run through the CBD table, giving r, e_one, e_two - the noise for",
    "this encryption, derived from m instead of picked independently.",
    "",
    "u and v get built with the normal formulas, then sent to Bob.",
]
draw_paragraph(2 * cm, text_y, WIDTH - 4 * cm, lines)
c.showPage()

# ---------------------------------------------------------------
# Page 3: Act 3 - Bob / Decapsulate
# ---------------------------------------------------------------
draw_title("Act 3: Bob's Decapsulate")

top = HEIGHT - 4.5 * cm
draw_box(2 * cm, top, box_w, box_h, "u, v", "received")
draw_arrow(2 * cm + box_w, top + box_h / 2, 7 * cm, top + box_h / 2, "algebra + S")
draw_box(7 * cm, top, box_w, box_h, "m_recovered", "recovered message")

draw_arrow(7 * cm + box_w / 2, top, 7 * cm + box_w / 2, top - 1.5 * cm, "re-hash")
draw_box(7 * cm, top - 3 * cm, box_w, box_h, "K', r_coins'", "same 2-step hash")

draw_arrow(7 * cm + box_w / 2, top - 3 * cm, 7 * cm + box_w / 2, top - 4.5 * cm, "regenerate")
draw_box(7 * cm, top - 6 * cm, box_w, box_h, "u', v'", "rebuilt ciphertext")

draw_arrow(7 * cm + box_w, top - 6 * cm + box_h / 2, 12.5 * cm, top - 6 * cm + box_h / 2, "compare")
draw_box(12.5 * cm, top - 6 * cm, box_w, box_h, "match?", "u'==u and v'==v")

text_y = top - 8.5 * cm
lines = [
    "Bob uses his private S against the (u, v) he received to recover",
    "m_recovered - pure algebra, same as the very first toy build.",
    "",
    "Bob re-hashes (m_recovered + H(ek)) - reusing his already-stored H(ek)",
    "instead of recomputing it - and gets K' and r_coins' the same way",
    "Alice did.",
    "",
    "r_coins' regenerates r', e_one', e_two', which rebuild what u and v",
    "should have looked like, using Bob's own A and b.",
    "",
    "If the rebuilt (u', v') matches the real (u, v) Alice sent, K' is",
    "confirmed as the genuine shared secret - and it matches Alice's K",
    "exactly. (The fallback for a mismatch isn't built yet.)",
]
draw_paragraph(2 * cm, text_y, WIDTH - 4 * cm, lines)
c.showPage()

# ---------------------------------------------------------------
# Page 4: Act 4 - AES-256 starting key matrix
# ---------------------------------------------------------------
draw_title("Act 4: AES-256 Starting Key Matrix")

top = HEIGHT - 4.5 * cm
draw_box(2 * cm, top, box_w, box_h, "K_final", "32 bytes")
draw_arrow(2 * cm + box_w, top + box_h / 2, 8 * cm, top + box_h / 2, "arrange")

grid_x, grid_y = 9.5 * cm, top
cell = 0.9 * cm
for row in range(4):
    for col in range(8):
        x = grid_x + col * cell
        y = grid_y + box_h / 2 - (row - 1.5) * cell - cell / 2
        c.rect(x, y, cell, cell, stroke=1, fill=0)

c.setFont("Helvetica", 9)
c.drawString(9.5 * cm, top - 2.2 * cm, "4 rows x 8 columns of bytes (4 x 8 = 32)")

text_y = top - 4 * cm
lines = [
    "K_final is 32 bytes - the real, confirmed shared secret from Act 3.",
    "",
    "AES-256 needs its key arranged into a grid before the key schedule",
    "can expand it: 4 rows by 8 columns of bytes (4 x 8 = 32, exactly the",
    "size of K_final).",
    "",
    "Bytes fill DOWN each column first, then move to the next column -",
    "AES's standard fill order. So byte 0 goes to row 0/col 0, byte 1 to",
    "row 1/col 0, byte 2 to row 2/col 0, byte 3 to row 3/col 0, byte 4",
    "starts the next column at row 0/col 1, and so on.",
    "",
    "This 4x8 grid is where AES-256's key schedule (turning one key into",
    "15 separate round keys) would start - not built yet, next piece.",
]
draw_paragraph(2 * cm, text_y, WIDTH - 4 * cm, lines)
c.showPage()

c.save()
print("saved to", OUT_PATH)
