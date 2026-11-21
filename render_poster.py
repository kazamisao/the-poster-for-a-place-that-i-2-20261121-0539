"""Render the LUMORA travel poster (1024x1024) with Pillow.

Concept (own design, following the advisor's direction): LUMORA — a bay
where a giant golden disc half-sinks into the sea, "a sun gone
swimming". Warm dusk after rain; the disc throws a path of light to
the shore. One landmark only, no clutter. Palette: night blue #173B52,
coral #ED8975, gold #FFD477, cream #FFF1D6.

Supersampled 2x (2048) then downscaled with LANCZOS. Deterministic:
seeded random only; same bytes every run.
"""
import os
import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = 2048  # supersample size; final is 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "poster.png")

NIGHT = (23, 59, 82)      # #173B52
CORAL = (237, 137, 117)   # #ED8975
GOLD = (255, 212, 119)    # #FFD477
GOLD_DEEP = (245, 166, 35)
CREAM = (255, 241, 214)   # #FFF1D6
SAND = (246, 223, 174)
SEA_DEEP = (16, 46, 61)

def _font(*candidates):
    """First existing font path wins; fail loudly naming every miss."""
    for path in candidates:
        if os.path.exists(path):
            return path
    raise SystemExit(f"missing font: none of {candidates} found")


FONT_DISPLAY = _font(
    "/usr/share/fonts/truetype/noto/NotoSansDisplay-Black.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
)
FONT_BOLD = _font(
    "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
)

HORIZON = int(S * 0.62)          # y of the horizon
DISC_C = (S // 2, 1130)          # disc centre (just above horizon)
DISC_R = 330


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vertical_gradient(size, stops):
    """stops: list of (position 0..1, rgb). Returns an RGB image."""
    w, h = size
    img = Image.new("RGB", (1, h))
    px = img.load()
    for y in range(h):
        t = y / (h - 1)
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                px[0, y] = lerp(c0, c1, 0 if p1 == p0 else (t - p0) / (p1 - p0))
                break
        else:
            px[0, y] = stops[-1][1]
    return img.resize((w, h))


def draw_tracked(draw, xy_center, text, font, fill, tracking, stroke_w=0, stroke_fill=None):
    """Draw text centred at xy_center with letter tracking (px between glyphs)."""
    widths = []
    total = 0
    for ch in text:
        w = draw.textlength(ch, font=font)
        widths.append(w)
        total += w
    total += tracking * (len(text) - 1)
    x = xy_center[0] - total / 2
    y = xy_center[1]
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill,
                  stroke_width=stroke_w, stroke_fill=stroke_fill)
        x += w + tracking
    return total


def fit_font(draw, text, path, start_size, max_width, tracking_ratio=0.08):
    size = start_size
    while size > 40:
        font = ImageFont.truetype(path, size)
        w = sum(draw.textlength(ch, font=font) for ch in text)
        w += size * tracking_ratio * (len(text) - 1)
        if w <= max_width:
            return font, size * tracking_ratio
        size -= 10
    font = ImageFont.truetype(path, size)
    return font, size * tracking_ratio


def main():
    rng = random.Random(20261121)
    img = Image.new("RGB", (S, S))

    # --- sky + sea base gradients -------------------------------------
    sky = vertical_gradient((S, HORIZON), [
        (0.00, NIGHT), (0.30, (39, 88, 110)), (0.52, (185, 106, 94)),
        (0.80, CORAL), (1.00, (240, 150, 110)),
    ])
    img.paste(sky, (0, 0))
    sea = vertical_gradient((S, S - HORIZON), [
        (0.00, (224, 138, 103)), (0.12, (120, 92, 96)),
        (0.35, (42, 74, 88)), (1.00, SEA_DEEP),
    ])
    img.paste(sea, (0, HORIZON))

    # --- glow halo around the disc ------------------------------------
    halo = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    for i in range(14, 0, -1):
        r = DISC_R + i * 26
        alpha = int(10 + (14 - i) * 2)
        hd.ellipse([DISC_C[0] - r, DISC_C[1] - r, DISC_C[0] + r, DISC_C[1] + r],
                   fill=GOLD + (alpha,))
    halo = halo.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img.convert("RGBA"), halo)

    # --- the golden disc (vertical gradient, clipped to circle) -------
    disc = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    grad = vertical_gradient((DISC_R * 2, DISC_R * 2), [
        (0.0, (255, 233, 168)), (0.45, GOLD), (1.0, GOLD_DEEP),
    ]).convert("RGBA")
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).ellipse(
        [DISC_C[0] - DISC_R, DISC_C[1] - DISC_R,
         DISC_C[0] + DISC_R, DISC_C[1] + DISC_R], fill=255)
    disc.paste(grad, (DISC_C[0] - DISC_R, DISC_C[1] - DISC_R), mask.crop(
        (DISC_C[0] - DISC_R, DISC_C[1] - DISC_R,
         DISC_C[0] + DISC_R, DISC_C[1] + DISC_R)))
    # thin bright rim on the disc's upper edge
    rim = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(rim).arc(
        [DISC_C[0] - DISC_R, DISC_C[1] - DISC_R,
         DISC_C[0] + DISC_R, DISC_C[1] + DISC_R],
        start=195, end=345, fill=(255, 244, 200, 220), width=10)
    img = Image.alpha_composite(img, disc)
    img = Image.alpha_composite(img, rim)

    # --- the disc half-submerged: dim its lower half with a translucent
    # copy of the sea, as if seen through the water surface ------------
    sea_cover = Image.new("RGBA", (S, S - HORIZON), (0, 0, 0, 0))
    sea_grad = vertical_gradient((S, S - HORIZON), [
        (0.00, (224, 138, 103)), (0.12, (120, 92, 96)),
        (0.35, (42, 74, 88)), (1.00, SEA_DEEP),
    ]).convert("RGBA")
    sea_cover.paste(sea_grad, (0, 0))
    alpha = sea_cover.split()[3].point(lambda a: int(a * 0.82))
    sea_cover.putalpha(alpha)
    cover = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cover.paste(sea_cover, (0, HORIZON))
    img = Image.alpha_composite(img, cover)

    d = ImageDraw.Draw(img, "RGBA")

    # --- soft clouds in the upper sky ----------------------------------
    clouds = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cd = ImageDraw.Draw(clouds)
    for (cx, cy, cw, ch, a) in [
            (420, 760, 620, 46, 46), (1500, 700, 700, 52, 40),
            (1150, 560, 520, 40, 34), (300, 980, 480, 36, 30),
            (1760, 1010, 420, 34, 28)]:
        cd.ellipse([cx - cw // 2, cy - ch // 2, cx + cw // 2, cy + ch // 2],
                   fill=(255, 226, 200, a))
    clouds = clouds.filter(ImageFilter.GaussianBlur(22))
    img = Image.alpha_composite(img, clouds)
    d = ImageDraw.Draw(img, "RGBA")

    # --- birds ----------------------------------------------------------
    for (bx, by, s) in [(300, 770, 26), (400, 740, 20), (1650, 760, 24),
                        (1760, 735, 17), (1560, 785, 15)]:
        d.arc([bx - s, by - s // 2, bx, by + s // 2], 200, 340,
              fill=NIGHT + (235,), width=5)
        d.arc([bx, by - s // 2, bx + s, by + s // 2], 200, 340,
              fill=NIGHT + (235,), width=5)

    # --- golden reflection path on the sea ------------------------------
    refl = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    rd = ImageDraw.Draw(refl)
    y = HORIZON + 8
    while y < S - 130:
        depth = (y - HORIZON) / (S - HORIZON)
        half_w = 110 + depth * 330
        cx = DISC_C[0] + rng.uniform(-1, 1) * half_w * 0.35
        length = rng.uniform(40, 150) + depth * 220
        alpha = int(rng.uniform(50, 150) * (1 - depth * 0.45))
        wdt = int(4 + depth * 10)
        rd.line([cx - length / 2, y, cx + length / 2, y],
                fill=GOLD + (alpha,), width=wdt)
        y += int(rng.uniform(12, 26))
    refl = refl.filter(ImageFilter.GaussianBlur(3))
    img = Image.alpha_composite(img, refl)
    d = ImageDraw.Draw(img, "RGBA")

    # --- beaches curving in from the bottom corners --------------------
    sand_layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sand_layer)
    # left beach: big ellipse whose top edge sweeps up toward the centre
    sd.ellipse([-620, 1620, 980, 2360], fill=SAND + (255,))
    sd.ellipse([1068, 1620, 2668, 2360], fill=SAND + (255,))
    # wet-sand edge along each beach curve
    sd.arc([-620, 1620, 980, 2360], start=270, end=360,
           fill=(232, 200, 143, 255), width=14)
    sd.arc([1068, 1620, 2668, 2360], start=180, end=270,
           fill=(232, 200, 143, 255), width=14)
    # foam line where the sea meets the sand
    sd.arc([-620, 1620, 980, 2360], start=270, end=360,
           fill=(255, 250, 235, 200), width=5)
    sd.arc([1068, 1620, 2668, 2360], start=180, end=270,
           fill=(255, 250, 235, 200), width=5)
    img = Image.alpha_composite(img, sand_layer)
    d = ImageDraw.Draw(img, "RGBA")

    # --- wordmark + tagline -------------------------------------------
    title_font, tracking = fit_font(d, "LUMORA", FONT_DISPLAY, 430, 1560)
    draw_tracked(d, (S // 2, 150), "LUMORA", title_font, CREAM, tracking,
                 stroke_w=10, stroke_fill=NIGHT)
    tag_font = ImageFont.truetype(FONT_BOLD, 66)
    draw_tracked(d, (S // 2, 640), "WHERE THE SUN GOES SWIMMING",
                 tag_font, GOLD, 26)

    # --- thin poster border ---------------------------------------------
    d.rectangle([44, 44, S - 44, S - 44], outline=CREAM + (215,), width=8)

    # --- downscale, save ------------------------------------------------
    img = img.convert("RGB").resize((1024, 1024), Image.LANCZOS)
    img.save(OUT, optimize=True)
    print(f"wrote {OUT} {os.path.getsize(OUT)} bytes")


if __name__ == "__main__":
    main()
