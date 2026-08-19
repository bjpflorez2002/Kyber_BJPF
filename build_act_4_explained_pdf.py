import os

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

WIDTH, HEIGHT = A4
MARGIN = 2 * cm
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "act_4_explained.pdf")

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


# =================================================================
heading("Act 4: The AES-256 Starting Key Matrix")
body("The shortest Act by a long way. Everything hard is already done - Bob and Alice both")
body("hold the same 32 bytes. This Act does one thing: puts those bytes into the shape AES")
body("expects.")

gap(0.5 * cm)
sub("The code, all of it")
mono("aes_key_matrix = [[0] * 8 for _ in range(4)]")
mono("")
mono("for byte_index in range(32):")
mono("    row = byte_index % 4")
mono("    col = byte_index // 4")
mono("    aes_key_matrix[row][col] = K_final[byte_index]")

gap(0.5 * cm)
sub("Why 4 rows by 8 columns")
body("AES-256 uses a 32-byte key, and it lays that out as 4 rows by 8 columns (4 x 8 = 32).")
body("Each COLUMN is 4 bytes, which AES calls a word. So the key is 8 words wide.")
gap(0.2 * cm)
body("The ordinary AES state block is 4 x 4. The key here is twice that width because a")
body("256-bit key is twice the size of one 128-bit block.")

gap(0.5 * cm)
sub("The fill order - DOWN each column, not across each row")
gap(0.4 * cm)

# --- fill order diagram ---
cell = 1.35 * cm
grid_x = MARGIN + 1.5 * cm
grid_top = y

for row in range(4):
    for col in range(8):
        x = grid_x + col * cell
        yy = grid_top - row * cell
        c.rect(x, yy - cell, cell, cell, stroke=1, fill=0)
        byte_index = col * 4 + row
        c.setFont("Helvetica", 8.5)
        c.drawCentredString(x + cell / 2, yy - cell / 2 - 3, "byte %d" % byte_index)

# arrows showing the down-then-across order
c.setFont("Helvetica-Bold", 8)
for col in range(3):
    ax = grid_x + col * cell + cell / 2
    c.setDash(2, 2)
    c.line(ax, grid_top - 0.15 * cm, ax, grid_top - 4 * cell + 0.15 * cm)
    c.setDash()
    c.line(ax, grid_top - 4 * cell + 0.15 * cm, ax - 3, grid_top - 4 * cell + 0.35 * cm)
    c.line(ax, grid_top - 4 * cell + 0.15 * cm, ax + 3, grid_top - 4 * cell + 0.35 * cm)

y = grid_top - 4 * cell - 0.8 * cm

body("Byte 0 goes to row 0 column 0. Byte 1 to row 1 column 0. Byte 2 to row 2, byte 3 to")
body("row 3 - filling the first column top to bottom. Then byte 4 starts the next column")
body("back at row 0, and so on across all 8 columns.")
gap(0.3 * cm)
body("That is exactly what the two lines of arithmetic do:")
mono("row = byte_index % 4     ->  cycles 0,1,2,3, 0,1,2,3, ...")
mono("col = byte_index // 4    ->  advances every 4 bytes: 0,0,0,0, 1,1,1,1, ...")

new_page()

heading("What Act 4 is, and what it is not")

sub("There is only ONE key")
body("aes_key_matrix is not a new or separate thing. It contains exactly the same 32 bytes")
body("as K_final, just drawn out in a grid instead of a line. Read the grid back down each")
body("column and you get K_final again, byte for byte identical.")
gap(0.3 * cm)
body("K_final IS the AES starting key. The matrix is a picture of it.")

gap(0.6 * cm)
sub("Where this matters - and where it does not")
gap(0.2 * cm)
body("IF BUILDING AES FROM SCRATCH: this grid is genuinely the starting point. The AES key")
body("schedule works column by column on exactly this layout, expanding these 8 columns")
body("into the 60 columns needed for all 15 round keys.")
gap(0.3 * cm)
body("IF USING A LIBRARY: the library wants the plain 32 bytes and builds its own internal")
body("layout. It never sees this grid. In that case Act 4 demonstrates that you understand")
body("the format, but it is not a step the library actually performs.")
gap(0.3 * cm)
body("Worth being straight about that distinction in a write-up rather than implying the")
body("matrix is doing work it is not.")

gap(0.6 * cm)
sub("The handover point")
body("Act 4 is where ML-KEM finishes and AES begins. Everything before it - the lattices,")
body("the noise, the NTT, the compression, the re-encryption check - existed for one")
body("purpose: getting two strangers to hold the same 32 bytes without ever sending them.")
gap(0.3 * cm)
body("From here on the maths is completely different and belongs to AES, not Kyber.")

gap(0.6 * cm)
sub("What is NOT built yet")
body("- the AES key schedule (turning these 8 columns into 15 round keys)")
body("- the AES cipher itself (SubBytes, ShiftRows, MixColumns, AddRoundKey)")
body("- encrypting or decrypting an actual message")
gap(0.3 * cm)
body("Act 4 produces a correctly shaped key and stops there. Nothing has been encrypted.")

c.save()
print("saved to", OUT_PATH)
