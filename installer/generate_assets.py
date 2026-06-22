"""
Generate Inno Setup wizard images and icon for Screen Clean installer.
Run: python installer/generate_assets.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).parent / "assets"
OUT.mkdir(parents=True, exist_ok=True)

BG = (12, 11, 10)
ACCENT = (255, 90, 31)
ACCENT_SOFT = (255, 122, 69)
TEXT = (245, 243, 240)


def _font(size: int, bold: bool = False):
    names = ["segoeui.ttf", "segoeuib.ttf"] if bold else ["segoeui.ttf", "arial.ttf"]
    for name in ([names[1], names[0]] if bold else names):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _gradient_bg(w: int, h: int) -> Image.Image:
    img = Image.new("RGB", (w, h), BG)
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(h - 1, 1)
        r = int(BG[0] + (28 - BG[0]) * (1 - t) * 0.35)
        g = int(BG[1] + (24 - BG[1]) * (1 - t) * 0.35)
        b = int(BG[2] + (20 - BG[2]) * (1 - t) * 0.35)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse([w // 2 - 90, h // 3 - 60, w // 2 + 90, h // 3 + 100], fill=(255, 90, 31, 38))
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, glow)
    return img.convert("RGB")


def wizard_large():
    w, h = 164, 314
    img = _gradient_bg(w, h)
    draw = ImageDraw.Draw(img)
    cx, cy = w // 2, h // 2 - 20
    draw.ellipse([cx - 42, cy - 42, cx + 42, cy + 42], fill=ACCENT_SOFT)
    draw.ellipse([cx - 38, cy - 38, cx + 38, cy + 38], fill=ACCENT)
    font = _font(22, bold=True)
    draw.text((cx, cy), "SC", fill=(26, 18, 8), font=font, anchor="mm")
    title = _font(13, bold=True)
    draw.text((cx, cy + 58), "Screen Clean", fill=TEXT, font=title, anchor="mm")
    sub = _font(9)
    draw.text((cx, cy + 78), "Desktop sorting", fill=(180, 175, 168), font=sub, anchor="mm")
    img.save(OUT / "wizard-large.bmp", "BMP")


def wizard_small():
    size = 55
    img = Image.new("RGB", (size, size), BG)
    draw = ImageDraw.Draw(img)
    m = 4
    draw.rounded_rectangle([m, m, size - m, size - m], radius=12, fill=ACCENT)
    font = _font(16, bold=True)
    draw.text((size // 2, size // 2), "SC", fill=(26, 18, 8), font=font, anchor="mm")
    img.save(OUT / "wizard-small.bmp", "BMP")


def app_icon():
    sizes = [16, 24, 32, 48, 64, 128, 256]
    images = []
    for s in sizes:
        img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        pad = max(1, s // 10)
        draw.rounded_rectangle([pad, pad, s - pad, s - pad], radius=max(4, s // 5), fill=ACCENT + (255,))
        font = _font(max(8, s // 3), bold=True)
        draw.text((s // 2, s // 2), "SC", fill=(26, 18, 8, 255), font=font, anchor="mm")
        images.append(img)
    images[0].save(
        OUT / "icon.ico",
        format="ICO",
        sizes=[(s, s) for s in sizes],
        append_images=images[1:],
    )


if __name__ == "__main__":
    wizard_large()
    wizard_small()
    app_icon()
    print(f"Installer assets saved to {OUT}")
