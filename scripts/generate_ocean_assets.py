"""Generate the animated ocean assets used by the GitHub profile README."""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

WIDTH, HEADER_H, HEADER_FRAMES = 1400, 340, 24
WAVE_H, WAVE_FRAMES = 140, 24
SONAR_SIZE, SONAR_FRAMES = 460, 36

BG_TOP = (2, 18, 31)
BG_BOTTOM = (0, 76, 105)
CYAN = (85, 230, 255)
SEA = (0, 168, 204)
FOAM = (232, 251, 255)
MUTED = (119, 175, 199)


def lerp(a, b, t):
    return tuple(int(x + (y - x) * t) for x, y in zip(a, b))


def font(size: int, bold: bool = False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def gradient(size):
    w, h = size
    img = Image.new("RGB", size)
    px = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        c = lerp(BG_TOP, BG_BOTTOM, t)
        for x in range(w):
            px[x, y] = c
    return img


def glow_text(base, xy, text, fnt, fill=FOAM):
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.text(xy, text, font=fnt, fill=(*CYAN, 180), stroke_width=2, stroke_fill=(*SEA, 120))
    glow = glow.filter(ImageFilter.GaussianBlur(10))
    base.paste(glow, (0, 0), glow)
    d = ImageDraw.Draw(base)
    d.text(xy, text, font=fnt, fill=fill)


def wave_points(width, y0, amp, wavelength, phase, step=12):
    pts = []
    for x in range(-50, width + 60, step):
        y = y0 + amp * math.sin((x / wavelength) * 2 * math.pi + phase)
        pts.append((x, y))
    return pts


def header_frame(i):
    im = gradient((WIDTH, HEADER_H)).convert("RGBA")
    d = ImageDraw.Draw(im, "RGBA")

    # subtle depth grid
    for y in range(35, HEADER_H, 35):
        d.line((0, y, WIDTH, y), fill=(120, 230, 255, 12), width=1)
    for x in range(0, WIDTH, 70):
        d.line((x, 0, x, HEADER_H), fill=(120, 230, 255, 7), width=1)

    # drifting particles
    for n in range(56):
        x = (n * 97 + i * 9) % WIDTH
        y = 24 + (n * 53) % 190
        r = 1 if n % 4 else 2
        a = 50 + (n * 17) % 85
        d.ellipse((x-r, y-r, x+r, y+r), fill=(*CYAN, a))

    # title / subtitle
    title = font(62, True)
    sub = font(22, False)
    title_text = "DHVANIT SHAH"
    bbox = d.textbbox((0, 0), title_text, font=title)
    tw = bbox[2] - bbox[0]
    glow_text(im, ((WIDTH-tw)//2, 55), title_text, title)
    subtitle = "ICT STUDENT  •  CODE EXPLORER  •  SYSTEM BUILDER"
    sb = d.textbbox((0, 0), subtitle, font=sub)
    sw = sb[2] - sb[0]
    d.text(((WIDTH-sw)//2, 132), subtitle, font=sub, fill=(*MUTED, 255))

    # telemetry bar
    d.rounded_rectangle((410, 175, 990, 211), radius=18, outline=(*SEA, 80), fill=(0, 15, 28, 110), width=1)
    d.text((435, 183), "SIGNAL", font=font(13, True), fill=(*CYAN, 240))
    d.text((520, 183), "DEEP CODE CHANNEL", font=font(13, True), fill=(*FOAM, 230))
    progress = int(390 * (0.5 + 0.5 * math.sin(i / 6)))
    d.rounded_rectangle((555, 188, 955, 200), radius=6, fill=(3, 46, 63, 255))
    d.rounded_rectangle((555, 188, 555 + max(12, progress), 200), radius=6, fill=(*SEA, 220))

    # wave layers
    overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay, "RGBA")
    for idx, (y0, amp, wl, col, alpha) in enumerate([
        (255, 25, 260, (0, 231, 255), 70),
        (270, 18, 330, (0, 168, 204), 100),
        (292, 24, 420, (0, 105, 148), 190),
    ]):
        pts = wave_points(WIDTH, y0, amp, wl, i * 0.28 + idx * 0.9)
        polygon = [(pts[0][0], HEADER_H), *pts, (pts[-1][0], HEADER_H)]
        od.polygon(polygon, fill=(*col, alpha))
    im.alpha_composite(overlay)

    return im.convert("P", palette=Image.Palette.ADAPTIVE)


def wave_frame(i):
    im = Image.new("RGBA", (WIDTH, WAVE_H), (*BG_TOP, 255))
    overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay, "RGBA")
    layers = [
        (55, 15, 250, (0, 105, 148), 190),
        (68, 14, 310, (0, 168, 204), 200),
        (85, 19, 390, (85, 230, 255), 175),
        (102, 14, 470, (0, 85, 125), 230),
    ]
    for idx, (y0, amp, wl, col, alpha) in enumerate(layers):
        pts = wave_points(WIDTH, y0, amp, wl, i * 0.34 + idx)
        d.polygon([(pts[0][0], WAVE_H), *pts, (pts[-1][0], WAVE_H)], fill=(*col, alpha))
    # bubbles
    for n in range(18):
        x = (n * 83 + i * 5) % WIDTH
        y = 18 + ((n * 29 - i * 3) % 88)
        r = 2 + n % 3
        d.ellipse((x-r, y-r, x+r, y+r), outline=(*FOAM, 110), width=1)
    im.alpha_composite(overlay)
    return im.convert("P", palette=Image.Palette.ADAPTIVE)


def sonar_frame(i):
    S = SONAR_SIZE
    im = Image.new("RGBA", (S, S), (*BG_TOP, 255))
    d = ImageDraw.Draw(im, "RGBA")
    c = S // 2
    # rings
    for r, alpha in [(195, 42), (150, 50), (105, 58), (60, 70)]:
        d.ellipse((c-r, c-r, c+r, c+r), outline=(*CYAN, alpha), width=2)
    for a in range(0, 360, 45):
        rad = math.radians(a)
        x2 = c + int(195 * math.cos(rad))
        y2 = c + int(195 * math.sin(rad))
        d.line((c, c, x2, y2), fill=(*CYAN, 20), width=1)
    # targets
    targets = [(110, -55, 4), (-85, 70, 5), (35, 120, 4), (-120, -95, 3)]
    for j, (tx, ty, r) in enumerate(targets):
        x, y = c + tx, c + ty
        pulse = 1 + 0.4 * math.sin(i / 3 + j)
        rr = int(r * pulse + 2)
        d.ellipse((x-rr, y-rr, x+rr, y+rr), fill=(*CYAN, 220))
    # sweep ray
    angle = math.radians((i * 12) % 360)
    x2 = c + int(195 * math.cos(angle))
    y2 = c + int(195 * math.sin(angle))
    d.line((c, c, x2, y2), fill=(*FOAM, 170), width=3)
    # label
    d.text((24, 20), "SONAR // DIVE LOG", font=font(16, True), fill=(*FOAM, 210))
    d.text((24, 42), f"PASS {i+1:02d}  •  SIGNAL ACTIVE", font=font(12, False), fill=(*MUTED, 220))
    return im.convert("P", palette=Image.Palette.ADAPTIVE)


def save_animation(frames, path, duration):
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=duration, loop=0, optimize=True, disposal=2)


def main():
    save_animation([header_frame(i) for i in range(HEADER_FRAMES)], ASSETS / "ocean-header.gif", 90)
    save_animation([wave_frame(i) for i in range(WAVE_FRAMES)], ASSETS / "ocean-wave.gif", 80)
    save_animation([sonar_frame(i) for i in range(SONAR_FRAMES)], ASSETS / "sonar.gif", 75)

    # Self-contained animated SVG divider, useful on GitHub and local previews.
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 120" role="img" aria-label="Animated ocean wave divider">
      <defs>
        <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#031b2d"/><stop offset="1" stop-color="#001018"/></linearGradient>
        <linearGradient id="w" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#006994"/><stop offset=".5" stop-color="#55e6ff"/><stop offset="1" stop-color="#006994"/></linearGradient>
      </defs>
      <rect width="1400" height="120" fill="url(#bg)"/>
      <g fill="none" stroke-linecap="round">
        <path d="M0 70 Q175 30 350 70 T700 70 T1050 70 T1400 70" stroke="url(#w)" stroke-width="8" opacity=".55">
          <animateTransform attributeName="transform" type="translate" from="0 0" to="-350 0" dur="7s" repeatCount="indefinite"/>
        </path>
        <path d="M0 82 Q175 42 350 82 T700 82 T1050 82 T1400 82" stroke="#00a8cc" stroke-width="5" opacity=".75">
          <animateTransform attributeName="transform" type="translate" from="0 0" to="-350 0" dur="5.5s" repeatCount="indefinite"/>
        </path>
        <path d="M0 94 Q175 54 350 94 T700 94 T1050 94 T1400 94" stroke="#55e6ff" stroke-width="3" opacity=".85">
          <animateTransform attributeName="transform" type="translate" from="0 0" to="-350 0" dur="4.4s" repeatCount="indefinite"/>
        </path>
      </g>
    </svg>'''
    (ASSETS / "ocean-divider.svg").write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    main()
