"""Placeholder screenshot generator.

Renders fake-but-realistic landing-page screenshots so the renderer can be
previewed without the actual Lovable preview URLs. Replaced in Phase 2 by
real screenshots captured from `get_project` and Playwright.
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from .config import FONT_REG, FONT_BOLD


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def _grad(size: tuple[int, int], a: tuple[int, int, int],
          b: tuple[int, int, int]) -> Image.Image:
    W, H = size
    img = Image.new("RGB", size, a)
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / max(H - 1, 1)
        c = tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)
    return img


def _topbar(d: ImageDraw.ImageDraw, W: int, brand: str,
            fg: tuple[int, int, int]) -> None:
    d.text((48, 30), brand, font=_font(28, bold=True), fill=fg)
    nav = ["Story", "Products", "About", "Contact"]
    x = W - 60
    for label in reversed(nav):
        tw = d.textbbox((0, 0), label, font=_font(20))[2]
        x -= tw + 28
        d.text((x, 36), label, font=_font(20), fill=fg)


def make_hero(path: Path, *, brand: str = "Auréa",
              headline: str = "Feed Your Skin,\nFind Your Glow.",
              body: str = ("Enhance Your Radiance with Clean, Science-Driven "
                           "Skincare — Cruelty-Free, Sustainable, and "
                           "Enriched with Antioxidants for Healthy Skin."),
              cta: str = "Order Now") -> Path:
    W, H = 1080, 1400
    bg = _grad((W, H), (227, 232, 220), (199, 211, 192))
    d = ImageDraw.Draw(bg)
    _topbar(d, W, brand, (40, 50, 40))

    d.multiline_text((80, 220), headline, font=_font(74, bold=True),
                     fill=(20, 30, 22), spacing=4)
    for i, line in enumerate(_wrap(body, _font(22), W - 160, d)):
        d.text((80, 470 + i * 32), line, font=_font(22), fill=(70, 80, 70))

    btn_y = 640
    btn_w, btn_h = 200, 56
    d.rounded_rectangle((80, btn_y, 80 + btn_w, btn_y + btn_h),
                        radius=14, fill=(20, 30, 22))
    d.text((80 + btn_w // 2, btn_y + btn_h // 2), cta,
           font=_font(22, bold=True), fill=(255, 255, 255), anchor="mm")

    bottle_cx, bottle_cy = W // 2, 1080
    d.ellipse((bottle_cx - 220, bottle_cy + 180, bottle_cx + 220,
               bottle_cy + 250), fill=(160, 170, 150))
    d.rounded_rectangle((bottle_cx - 90, bottle_cy - 200, bottle_cx + 90,
                         bottle_cy + 180), radius=18, fill=(60, 45, 30))
    d.rounded_rectangle((bottle_cx - 70, bottle_cy - 60, bottle_cx + 70,
                         bottle_cy + 100), radius=8, fill=(240, 235, 220))
    d.text((bottle_cx, bottle_cy + 20), brand, font=_font(28, bold=True),
           fill=(60, 60, 50), anchor="mm")
    bg.save(path, optimize=True)
    return path


def make_features(path: Path) -> Path:
    W, H = 1080, 1500
    bg = Image.new("RGB", (W, H), (243, 240, 232))
    d = ImageDraw.Draw(bg)

    band_h = 220
    d.rectangle((0, 0, W, band_h), fill=(120, 140, 110))
    d.text((W // 2, 80), "Trusted by over 10,000+ clients since 2018.",
           font=_font(22), fill=(240, 240, 230), anchor="mm")
    d.text((W * 0.32, 150), "4.8", font=_font(64, bold=True),
           fill=(255, 255, 255), anchor="mm")
    d.text((W * 0.32, 195), "★ ★ ★ ★ ★", font=_font(20),
           fill=(255, 220, 130), anchor="mm")
    d.text((W * 0.68, 150), "1.7M", font=_font(64, bold=True),
           fill=(255, 255, 255), anchor="mm")
    d.text((W * 0.68, 195), "products / year", font=_font(18),
           fill=(220, 220, 210), anchor="mm")

    d.text((W // 2, band_h + 70), "— Benefits —", font=_font(18),
           fill=(120, 140, 110), anchor="mm")
    d.text((W // 2, band_h + 130),
           "Healthy Skin Means a Healthier You",
           font=_font(32, bold=True), fill=(40, 50, 40), anchor="mm")

    img_x = 60
    img_y = band_h + 200
    img_w = 380
    img_h = 460
    d.rounded_rectangle((img_x, img_y, img_x + img_w, img_y + img_h),
                        radius=16, fill=(220, 230, 215))
    bcx = img_x + img_w // 2
    bcy = img_y + img_h // 2
    d.rounded_rectangle((bcx - 50, bcy - 120, bcx + 50, bcy + 120),
                        radius=12, fill=(70, 55, 40))
    d.rounded_rectangle((bcx - 38, bcy - 28, bcx + 38, bcy + 70),
                        radius=6, fill=(240, 235, 220))

    fx = img_x + img_w + 40
    fy = img_y + 10
    feats = [
        ("Deep Hydration", "Locks in moisture."),
        ("Radiance Boost", "Revives dullness."),
        ("Skin Barrier", "Protects from stressors."),
        ("Natural", "Botanically-derived."),
    ]
    for title, sub in feats:
        d.text((fx, fy), title, font=_font(22, bold=True), fill=(40, 50, 40))
        d.text((fx, fy + 32), sub, font=_font(17), fill=(110, 110, 100))
        fy += 110

    bg.save(path, optimize=True)
    return path


def make_testimonials(path: Path) -> Path:
    W, H = 1080, 1500
    bg = Image.new("RGB", (W, H), (243, 240, 232))
    d = ImageDraw.Draw(bg)
    d.text((W // 2, 70), "— Testimonials —", font=_font(18),
           fill=(120, 140, 110), anchor="mm")
    d.text((W // 2, 130), "See what Our customers have to say",
           font=_font(32, bold=True), fill=(40, 50, 40), anchor="mm")

    quotes = [
        ("Emily R.", "★★★★★",
         "Best countless serums but Auréa Celestial Glow Serum is next level."),
        ("Tom F.", "★★★★★",
         "As someone with eczema I'm cautious with new products. Auréa works."),
        ("Dan E.", "★★★★★",
         "Skin feels like soft cashmere. The Overnight Mask transformed me."),
    ]
    card_w = W - 80
    card_h = 200
    y = 200
    for name, stars, txt in quotes:
        x = 40
        d.rounded_rectangle((x, y, x + card_w, y + card_h), radius=14,
                            fill=(255, 255, 255))
        d.ellipse((x + 24, y + 24, x + 60, y + 60), fill=(220, 220, 210))
        d.text((x + 76, y + 28), name, font=_font(20, bold=True),
               fill=(40, 50, 40))
        d.text((x + 76, y + 56), stars, font=_font(16), fill=(200, 160, 60))
        for j, ln in enumerate(_wrap(txt, _font(17), card_w - 60, d)):
            d.text((x + 30, y + 100 + j * 24), ln, font=_font(17),
                   fill=(80, 80, 70))
        y += card_h + 30

    cta_y = y + 30
    cta_h = 320
    d.rounded_rectangle((40, cta_y, W - 40, cta_y + cta_h), radius=16,
                        fill=(220, 230, 215))
    d.text((80, cta_y + 50), "Subscribe to our newsletter",
           font=_font(28, bold=True), fill=(40, 50, 40))
    d.text((80, cta_y + 100), "Join the Auréa community.",
           font=_font(18), fill=(90, 100, 90))
    d.rounded_rectangle((80, cta_y + 170, 600, cta_y + 220), radius=10,
                        fill=(255, 255, 255))
    d.text((96, cta_y + 184), "Enter your email", font=_font(16),
           fill=(160, 160, 155))
    d.rounded_rectangle((620, cta_y + 170, 760, cta_y + 220), radius=10,
                        fill=(40, 50, 40))
    d.text((690, cta_y + 195), "Subscribe", font=_font(16, bold=True),
           fill=(255, 255, 255), anchor="mm")

    bg.save(path, optimize=True)
    return path


def make_footer(path: Path, *, brand: str = "Auréa") -> Path:
    W, H = 1080, 1200
    bg = Image.new("RGB", (W, H), (228, 234, 220))
    d = ImageDraw.Draw(bg)

    bottle_cx = W // 2
    bottle_cy = 280
    d.ellipse((bottle_cx - 180, bottle_cy + 160, bottle_cx + 180,
               bottle_cy + 220), fill=(160, 170, 150))
    d.rounded_rectangle((bottle_cx - 80, bottle_cy - 160, bottle_cx + 80,
                         bottle_cy + 160), radius=16, fill=(70, 55, 40))
    d.rounded_rectangle((bottle_cx - 60, bottle_cy - 40, bottle_cx + 60,
                         bottle_cy + 80), radius=6, fill=(240, 235, 220))
    d.text((bottle_cx, bottle_cy + 20), brand, font=_font(22, bold=True),
           fill=(60, 60, 50), anchor="mm")

    d.text((60, 600), brand, font=_font(36, bold=True), fill=(40, 50, 40))
    d.text((60, 650), f"hi@{brand.lower()}.com",
           font=_font(17), fill=(80, 90, 80))
    d.text((60, 678), "Mon-Sat 8am-7pm GMT",
           font=_font(17), fill=(80, 90, 80))

    cols = [
        ("Navigation", ["Home", "Products", "Collection"]),
        ("Company", ["About", "Testimonials", "Subscribe"]),
        ("Resources", ["Privacy", "Terms"]),
    ]
    for i, (title, items) in enumerate(cols):
        x = 60 + i * 320
        y0 = 800
        d.text((x, y0), title, font=_font(18, bold=True),
               fill=(40, 50, 40))
        for j, item in enumerate(items):
            d.text((x, y0 + 36 + j * 28), item, font=_font(16),
                   fill=(80, 90, 80))

    d.line((60, 1080, W - 60, 1080), fill=(190, 200, 180), width=2)
    d.text((60, 1120), f"© 2026 {brand}", font=_font(15),
           fill=(120, 130, 120))

    bg.save(path, optimize=True)
    return path


def _wrap(text: str, fnt: ImageFont.FreeTypeFont, max_w: int,
          d: ImageDraw.ImageDraw) -> list[str]:
    out: list[str] = []
    for para in text.split("\n"):
        line: list[str] = []
        for w in para.split(" "):
            test = " ".join(line + [w])
            if d.textbbox((0, 0), test, font=fnt)[2] > max_w and line:
                out.append(" ".join(line))
                line = [w]
            else:
                line.append(w)
        if line:
            out.append(" ".join(line))
    return out


def make_placeholder_site(out_dir: Path, brand: str = "Auréa") -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = [
        make_hero(out_dir / "01-hero.png", brand=brand),
        make_features(out_dir / "02-features.png"),
        make_testimonials(out_dir / "03-testimonials.png"),
        make_footer(out_dir / "04-footer.png", brand=brand),
    ]
    return paths
