"""Draw the ai-excited-01 entry image: a giant golden koi leaping out of a
tiny teacup, reaching for the moon. Original artwork, drawn from scratch
with PIL primitives. Canvas 1024x1024, saved as entry.png next to this script."""
import math
import random
from PIL import Image, ImageDraw, ImageFilter

W = H = 1024
random.seed(20261116)

img = Image.new("RGB", (W, H), (8, 34, 52))
d = ImageDraw.Draw(img, "RGBA")

# ---------- night sky: vertical gradient, deep teal -> indigo ----------
top = (10, 42, 74)
bot = (4, 20, 38)
grad = Image.new("RGB", (1, H))
grad.putdata([tuple(int(top[c] + (bot[c] - top[c]) * y / (H - 1)) for c in range(3))
              for y in range(H)])
grad = grad.resize((W, H))
img.paste(grad, (0, 0))
d = ImageDraw.Draw(img, "RGBA")

# ---------- stars ----------
for _ in range(140):
    x = random.uniform(0, W)
    y = random.uniform(0, 620)
    r = random.uniform(0.6, 2.2)
    a = random.randint(90, 220)
    d.ellipse([x - r, y - r, x + r, y + r], fill=(220, 235, 255, a))

# ---------- moon glow + moon, top right ----------
mx, my = 845, 150
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
for r, a in ((260, 18), (200, 26), (150, 40), (110, 60)):
    gd.ellipse([mx - r, my - r, mx + r, my + r], fill=(255, 244, 200, a))
img.paste(Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB"), (0, 0))
d = ImageDraw.Draw(img, "RGBA")
d.ellipse([mx - 62, my - 62, mx + 62, my + 62], fill=(255, 248, 220, 255))
d.ellipse([mx - 62, my - 62, mx + 62, my + 62], outline=(230, 220, 170, 255), width=3)
for cx, cy, cr in ((mx - 22, my - 18, 12), (mx + 18, my + 8, 9), (mx + 2, my + 30, 7),
                   (mx - 30, my + 22, 6)):
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(238, 228, 190, 255))

# ---------- distant hills silhouette ----------
d.polygon([(0, 700), (180, 640), (380, 690), (560, 645), (760, 695), (1024, 650),
           (1024, 1024), (0, 1024)], fill=(7, 30, 46, 255))

# ---------- table: warm dark wood, bottom ----------
d.polygon([(0, 880), (1024, 830), (1024, 1024), (0, 1024)], fill=(74, 48, 28, 255))
d.polygon([(0, 880), (1024, 830), (1024, 848), (0, 898)], fill=(96, 62, 36, 255))
for x0 in (200, 430, 660, 880):
    d.line([(x0, 1024), (x0 + 40, 838)], fill=(52, 33, 18, 255), width=4)
d.ellipse([300, 800, 640, 950], fill=(255, 190, 90, 28))

# ---------- helpers ----------
def bezier3(p0, p1, p2, p3, n=90):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = ((1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0]
             + 3 * (1 - t) * t * t * p2[0] + t ** 3 * p3[0])
        y = ((1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1]
             + 3 * (1 - t) * t * t * p2[1] + t ** 3 * p3[1])
        pts.append((x, y))
    return pts

def tangent(spine, i):
    n = len(spine)
    x0, y0 = spine[max(0, i - 1)]
    x1, y1 = spine[min(n - 1, i + 1)]
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1.0
    return dx / L, dy / L

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def band_polygon(spine, radii):
    left, right = [], []
    for i, (x, y) in enumerate(spine):
        dx, dy = tangent(spine, i)
        nx, ny = -dy, dx
        r = radii[i]
        left.append((x + nx * r, y + ny * r))
        right.append((x - nx * r, y - ny * r))
    return left + right[::-1]

# ---------- koi spine: crescent, tail at cup, head high top-right ----------
spine = bezier3((410, 800), (360, 580), (540, 360), (795, 285), n=90)
radii = []
for i in range(len(spine)):
    t = i / (len(spine) - 1)
    r = 26 + 64 * math.sin(math.pi * (0.12 + 0.78 * t)) ** 0.8
    if t > 0.86:
        r *= 1 - (t - 0.86) / 0.14 * 0.18
    radii.append(r)
head_dir = tangent(spine, len(spine) - 1)  # ~ (0.96, -0.28)
# dorsal side normal (up-left), belly side normal (down-right)
dn = (head_dir[1], -head_dir[0])   # (-dy, dx) -> up-left at head
bn = (-head_dir[1], head_dir[0])   # down-right at head

# ---------- tail fan: two flowing forked prongs fanning up-left from the cup ----------
def tapered_band(p0, p1, p2, w0, w1, n=24):
    """A curved tapered band along a quadratic bezier, as a polygon."""
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
        pts.append((x, y))
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        x0, y0 = pts[max(0, i - 1)]
        x1, y1 = pts[min(n, i + 1)]
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L, dx / L
        w = w0 + (w1 - w0) * (i / n)
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    return left + right[::-1], pts

tail_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
td = ImageDraw.Draw(tail_layer)
tx, ty = spine[0]
# upper prong: sweeps up-left, long and elegant
poly, centre = tapered_band((tx, ty), (tx - 110, ty - 110), (tx - 235, ty - 150), 26, 4)
td.polygon(poly, fill=(255, 150, 50, 180))
td.line(centre, fill=(255, 225, 175, 190), width=3)
# lower prong: sweeps left, slightly down
poly, centre = tapered_band((tx, ty), (tx - 130, ty - 20), (tx - 250, ty + 30), 24, 4)
td.polygon(poly, fill=(255, 170, 70, 180))
td.line(centre, fill=(255, 225, 175, 190), width=3)
tail_layer = tail_layer.filter(ImageFilter.GaussianBlur(1.2))
img.paste(Image.alpha_composite(img.convert("RGBA"), tail_layer).convert("RGB"), (0, 0))
d = ImageDraw.Draw(img, "RGBA")

# ---------- koi body: gradient circles along spine ----------
body = Image.new("RGBA", (W, H), (0, 0, 0, 0))
bd = ImageDraw.Draw(body)
head_c = (255, 196, 80)
mid_c = (255, 140, 40)
tail_c = (232, 90, 20)
for i, ((x, y), r) in enumerate(zip(spine, radii)):
    t = i / (len(spine) - 1)
    col = (lerp_color(tail_c, mid_c, min(1.0, t * 1.6)) if t < 0.6
           else lerp_color(mid_c, head_c, (t - 0.6) / 0.4))
    bd.ellipse([x - r, y - r, x + r, y + r], fill=col + (255,))
body = body.filter(ImageFilter.GaussianBlur(0.6))
img.paste(Image.alpha_composite(img.convert("RGBA"), body).convert("RGB"), (0, 0))
d = ImageDraw.Draw(img, "RGBA")

# body mask for clipping overlays
mask = Image.new("L", (W, H), 0)
md = ImageDraw.Draw(mask)
md.polygon(band_polygon(spine, radii), fill=255)

# ---------- belly highlight along the belly (down-right) side ----------
belly = Image.new("RGBA", (W, H), (0, 0, 0, 0))
bld = ImageDraw.Draw(belly)
for i in range(len(spine) - 1):
    dx, dy = tangent(spine, i)
    nx, ny = -dy, dx  # down-right side at mid-body
    (x0, y0), (x1, y1) = spine[i], spine[i + 1]
    bld.line([(x0 + nx * radii[i] * 0.55, y0 + ny * radii[i] * 0.55),
              (x1 + nx * radii[i + 1] * 0.55, y1 + ny * radii[i + 1] * 0.55)],
             fill=(255, 235, 200, 110), width=int(radii[i] * 0.5))
belly = belly.filter(ImageFilter.GaussianBlur(6))
belly = Image.composite(belly, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask)
img.paste(Image.alpha_composite(img.convert("RGBA"), belly).convert("RGB"), (0, 0))
d = ImageDraw.Draw(img, "RGBA")

# ---------- scales: sparse, subtle, dorsal side only ----------
scales = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(scales)
for i in range(10, len(spine) - 12, 7):
    (x, y), r = spine[i], radii[i]
    dx, dy = tangent(spine, i)
    nx, ny = dy, -dx  # up-left (dorsal) side
    for k in (-1, 0, 1):
        sx = x + nx * r * 0.45 + dx * k * r * 0.42
        sy = y + ny * r * 0.45 + dy * k * r * 0.42
        rr = r * 0.24
        sd.arc([sx - rr, sy - rr, sx + rr, sy + rr], start=15, end=165,
               fill=(185, 65, 10, 120), width=3)
scales = Image.composite(scales, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask)
img.paste(Image.alpha_composite(img.convert("RGBA"), scales).convert("RGB"), (0, 0))
d = ImageDraw.Draw(img, "RGBA")

# ---------- dorsal fin: one wavy translucent band on the up-left edge ----------
dorsal = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dd = ImageDraw.Draw(dorsal)
inner, outer = [], []
for i in range(8, len(spine) - 10):
    (x, y), r = spine[i], radii[i]
    dx, dy = tangent(spine, i)
    nx, ny = dy, -dx  # up-left
    wave = 16 + 14 * math.sin(i * 0.55)
    inner.append((x + nx * r * 0.92, y + ny * r * 0.92))
    outer.append((x + nx * (r + wave + 12), y + ny * (r + wave + 12)))
dd.polygon(inner + outer[::-1], fill=(255, 120, 30, 200))
dorsal = dorsal.filter(ImageFilter.GaussianBlur(1.5))
img.paste(Image.alpha_composite(img.convert("RGBA"), dorsal).convert("RGB"), (0, 0))
d = ImageDraw.Draw(img, "RGBA")

# ---------- head: round it out with a gold ellipse ----------
hx, hy = spine[-1]
hdx, hdy = head_dir
head_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
hd = ImageDraw.Draw(head_layer)
# ellipse centred slightly ahead of the spine end, rotated to head direction
cx, cy = hx + hdx * 14, hy + hdy * 14
ang = math.degrees(math.atan2(hdy, hdx))
head_layer2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
h2 = ImageDraw.Draw(head_layer2)
h2.ellipse([cx - 62, cy - 48, cx + 62, cy + 48], fill=(255, 192, 75, 255))
head_layer2 = head_layer2.rotate(-ang, center=(cx, cy), resample=Image.BICUBIC)
head_layer = Image.alpha_composite(head_layer, head_layer2)
head_layer = head_layer.filter(ImageFilter.GaussianBlur(0.8))
img.paste(Image.alpha_composite(img.convert("RGBA"), head_layer).convert("RGB"), (0, 0))
d = ImageDraw.Draw(img, "RGBA")

# ---------- eye: big, on the dorsal side of the head, set back from snout ----------
ex = cx - hdx * 26 + dn[0] * 20
ey = cy - hdy * 26 + dn[1] * 20
d.ellipse([ex - 17, ey - 17, ex + 17, ey + 17], fill=(255, 255, 255, 255))
d.ellipse([ex - 9, ey - 9, ex + 9, ey + 9], fill=(20, 10, 5, 255))
d.ellipse([ex - 4, ey - 6, ex + 3, ey + 1], fill=(255, 255, 255, 255))
# ---------- mouth: small open oval at the snout tip ----------
snx, sny = cx + hdx * 56, cy + hdy * 56
d.ellipse([snx - 13, sny - 9, snx + 13, sny + 9], fill=(120, 40, 8, 255))
d.ellipse([snx - 8, sny - 5, snx + 8, sny + 5], fill=(60, 15, 5, 255))
# ---------- barbels sweeping back from the mouth ----------
for off, length in ((0, 95), (12, 75)):
    pts = [(snx - hdx * 4 + dn[0] * off, sny - hdy * 4 + dn[1] * off)]
    for s in range(1, 9):
        pts.append((snx - hdx * (4 + s * length / 8 * 0.8) + dn[0] * (off + s * 2),
                    sny - hdy * (4 + s * length / 8 * 0.8) + dn[1] * (off + s * 2)
                    + s * s * 0.9))
    d.line(pts, fill=(255, 200, 120, 220), width=4)
# ---------- gill curve (set well back from the eye) ----------
d.arc([cx - hdx * 62 - 24, cy - hdy * 62 - 24, cx - hdx * 62 + 24, cy - hdy * 62 + 24],
      start=290, end=70, fill=(200, 80, 15, 200), width=4)

# ---------- pectoral fin: small curved fin on the belly side below the head ----------
fin = Image.new("RGBA", (W, H), (0, 0, 0, 0))
fd = ImageDraw.Draw(fin)
fx = cx - hdx * 58 + bn[0] * 34
fy = cy - hdy * 58 + bn[1] * 34
fd.polygon([(fx, fy), (fx - hdx * 62 + bn[0] * 55, fy - hdy * 62 + bn[1] * 55),
            (fx - hdx * 88 + bn[0] * 30, fy - hdy * 88 + bn[1] * 30)],
           fill=(255, 160, 60, 190))
fin = fin.filter(ImageFilter.GaussianBlur(1.5))
img.paste(Image.alpha_composite(img.convert("RGBA"), fin).convert("RGB"), (0, 0))
d = ImageDraw.Draw(img, "RGBA")

# ---------- water splash: arcs + droplets in the AIR around the cup ----------
splash = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sp = ImageDraw.Draw(splash)
cxp, cyp = 400, 800
for (sx, sy, sr, a0, a1) in ((cxp - 100, cyp - 25, 65, 200, 330), (cxp + 85, cyp - 45, 85, 210, 340),
                             (cxp - 25, cyp - 115, 55, 180, 330), (cxp + 135, cyp + 5, 50, 230, 320)):
    sp.arc([sx - sr, sy - sr, sx + sr, sy + sr], start=a0, end=a1,
           fill=(190, 235, 255, 200), width=5)
# droplets trailing the leap, kept off the body
for _ in range(40):
    t = random.uniform(0.0, 0.7)
    bx, by = spine[int(t * (len(spine) - 1))]
    dx, dy = tangent(spine, int(t * (len(spine) - 1)))
    nx, ny = dy, -dx  # dorsal side
    dist = random.uniform(55, 130)
    ox, oy = nx * dist + random.uniform(-25, 25), ny * dist + random.uniform(-25, 25)
    r = random.uniform(2.5, 7)
    sp.ellipse([bx + ox - r, by + oy - r, bx + ox + r, by + oy + r],
               fill=(200, 240, 255, random.randint(150, 230)))
# splash crown: small droplets radiating from the cup mouth
for ang in range(205, 336, 12):
    a = math.radians(ang)
    dist = 70 + random.uniform(0, 45)
    x1 = cxp + math.cos(a) * dist
    y1 = cyp + math.sin(a) * dist * 0.55
    r = random.uniform(3, 7)
    sp.ellipse([x1 - r, y1 - r, x1 + r, y1 + r], fill=(210, 240, 255, 230))
splash = splash.filter(ImageFilter.GaussianBlur(0.8))
img.paste(Image.alpha_composite(img.convert("RGBA"), splash).convert("RGB"), (0, 0))
d = ImageDraw.Draw(img, "RGBA")

# ---------- teacup: small, tilted, bottom centre-left ----------
cup = Image.new("RGBA", (W, H), (0, 0, 0, 0))
cd = ImageDraw.Draw(cup)
cd.ellipse([300, 905, 520, 945], fill=(235, 240, 245, 255))
cd.ellipse([300, 905, 520, 940], fill=(250, 252, 255, 255))
cupbody = Image.new("RGBA", (W, H), (0, 0, 0, 0))
cbd = ImageDraw.Draw(cupbody)
cbd.polygon([(330, 830), (490, 830), (470, 925), (350, 925)], fill=(248, 250, 252, 255))
cbd.polygon([(330, 830), (490, 830), (486, 852), (334, 852)], fill=(30, 90, 140, 255))
for px in range(345, 480, 26):
    cbd.ellipse([px, 862, px + 12, 878], outline=(30, 90, 140, 255), width=3)
cbd.arc([478, 845, 540, 905], start=270, end=90, fill=(248, 250, 252, 255), width=12)
cbd.ellipse([334, 824, 486, 844], fill=(190, 120, 40, 255))
cupbody = cupbody.rotate(-8, center=(410, 880), resample=Image.BICUBIC)
cup = Image.alpha_composite(cup, cupbody)
cup = cup.filter(ImageFilter.GaussianBlur(0.5))
img.paste(Image.alpha_composite(img.convert("RGBA"), cup).convert("RGB"), (0, 0))
d = ImageDraw.Draw(img, "RGBA")

# ---------- steam curls above the cup ----------
steam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
std = ImageDraw.Draw(steam)
for sx0 in (360, 410, 460):
    pts = []
    for s in range(21):
        pts.append((sx0 + math.sin(s * 0.55) * 14, 815 - s * 7))
    std.line(pts, fill=(220, 235, 245, 110), width=6)
steam = steam.filter(ImageFilter.GaussianBlur(3))
img.paste(Image.alpha_composite(img.convert("RGBA"), steam).convert("RGB"), (0, 0))

# ---------- vignette: darken edges slightly ----------
vig = Image.new("L", (W, H), 0)
vd = ImageDraw.Draw(vig)
vd.ellipse([-220, -220, W + 220, H + 220], fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(180))
dark = Image.new("RGB", (W, H), (2, 8, 16))
img = Image.composite(img, dark, vig)

img.save("entry.png", optimize=True)
print("saved entry.png", img.size, len(open("entry.png", "rb").read()), "bytes")
