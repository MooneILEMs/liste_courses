from PIL import Image, ImageDraw
import math

PAPIER = (239, 241, 236, 255)
MARGE = (212, 69, 60, 140)
STYLO = (29, 63, 190, 255)

def make(size, path):
    img = Image.new("RGBA", (size, size), PAPIER)
    d = ImageDraw.Draw(img)

    marge_x = round(size * 0.22)
    marge_w = max(1, round(size * 0.03))
    d.rectangle([marge_x, 0, marge_x + marge_w, size], fill=MARGE)

    cx, cy = size * 0.40, size * 0.52
    w = max(2, round(size * 0.05))

    def thick_line(p1, p2, width, color):
        d.line([p1, p2], fill=color, width=width)
        r = width / 2
        for p in (p1, p2):
            d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=color)

    p1 = (cx - size * 0.14, cy)
    p2 = (cx, cy + size * 0.14)
    p3 = (cx + size * 0.28, cy - size * 0.22)

    thick_line(p1, p2, w, STYLO)
    thick_line(p2, p3, w, STYLO)

    img.save(path)

make(192, "docs/icon-192.png")
make(512, "docs/icon-512.png")
print("done")
