"""Generate Open Graph share image (1200x630)."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

W, H = 1200, 630
BG = (250, 248, 245)
GREEN = (46, 94, 62)
GOLD = (200, 149, 42)
DARK = (28, 28, 28)
GREY = (102, 102, 102)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

# Background subtle gradient circles
for r, alpha, cx, cy in [(550, 18, 1100, -50), (450, 14, -50, 700)]:
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*GREEN, alpha))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    d = ImageDraw.Draw(img)

# Logo: green rounded square
LOGO_X, LOGO_Y, LOGO_S = 100, 100, 96
d.rounded_rectangle(
    [LOGO_X, LOGO_Y, LOGO_X + LOGO_S, LOGO_Y + LOGO_S], radius=22, fill=GREEN
)
# M curve (8,27 8,14 14,20 19,11 24,20 30,14 30,27) scaled to logo
pts = [(8, 27), (8, 14), (14, 20), (19, 11), (24, 20), (30, 14), (30, 27)]
scale = LOGO_S / 38
scaled = [(LOGO_X + x * scale, LOGO_Y + y * scale) for x, y in pts]
d.line(scaled, fill="white", width=6, joint="curve")
# Gold accent dot
gx, gy = LOGO_X + 30 * scale, LOGO_Y + 27 * scale
d.ellipse([gx - 7, gy - 7, gx + 7, gy + 7], fill=GOLD)

# Fonts
FONTS = Path(__file__).parent / "fonts"
# Pillow can't easily render woff2, fall back to a system font
try:
    title_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Georgia.ttf", 78)
    title_italic = ImageFont.truetype("/System/Library/Fonts/Supplemental/Georgia Italic.ttf", 78)
    label_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 22)
    sub_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 28)
    brand_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Georgia.ttf", 32)
except OSError:
    title_font = title_italic = label_font = sub_font = brand_font = ImageFont.load_default()

# Brand name next to logo
d.text((LOGO_X + LOGO_S + 24, LOGO_Y + 30), "müllers büro", font=brand_font, fill=DARK)

# Label
d.text((100, 270), "BERATUNG · ENERGIEWIRTSCHAFT · BERLIN", font=label_font, fill=GREEN)

# Title
d.text((100, 310), "Andrej Müller –", font=title_font, fill=DARK)
d.text((100, 395), "Ihr Ansprechpartner", font=title_italic, fill=GREEN)
d.text((100, 480), "in der Energiebranche.", font=title_font, fill=DARK)

# Subtle URL bottom
d.text((100, H - 60), "muellers-buero.online", font=sub_font, fill=GREY)

out = Path(__file__).parent / "og-image.png"
img.save(out, "PNG", optimize=True)
print(f"wrote {out} ({out.stat().st_size} bytes)")
