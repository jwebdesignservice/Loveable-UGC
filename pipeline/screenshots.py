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


# ---------------------------------------------------------------- ugly sites


FONT_SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
FONT_SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"


def _ugly_font(size: int, *, bold: bool = False, serif: bool = True
               ) -> ImageFont.FreeTypeFont:
    if serif and bold:
        return ImageFont.truetype(FONT_SERIF_BOLD, size)
    if serif:
        return ImageFont.truetype(FONT_SERIF, size)
    return _font(size, bold=bold)


def make_ugly_hero(path: Path, *, brand: str, tagline: str,
                  blurb: str) -> Path:
    """A homepage that screams 2005. Yellow/teal bg, Times serif, blue
    underlined heading, garish CTA, bordered tables."""
    W, H = 1080, 1400
    bg = Image.new("RGB", (W, H), (255, 255, 204))
    d = ImageDraw.Draw(bg)

    d.rectangle((0, 0, W, 80), fill=(0, 102, 204))
    d.text((W // 2, 40), f"::: {brand.upper()} :::",
           font=_ugly_font(26, bold=True), fill=(255, 255, 0), anchor="mm")

    d.rectangle((0, 80, W, 130), fill=(255, 153, 0))
    nav = ["Home", "About Us", "Products", "Services", "Guestbook", "Contact"]
    x = 30
    for label in nav:
        d.text((x, 95), label, font=_ugly_font(18, bold=True),
               fill=(0, 0, 153))
        x += 175

    d.text((W // 2, 200),
           f"Welcome to {brand}!!!",
           font=_ugly_font(56, bold=True), fill=(0, 0, 180), anchor="mm")
    bb = d.textbbox((0, 0), f"Welcome to {brand}!!!",
                    font=_ugly_font(56, bold=True))
    underline_w = bb[2] - bb[0]
    d.line((W // 2 - underline_w // 2, 232, W // 2 + underline_w // 2, 232),
           fill=(0, 0, 180), width=3)

    d.text((W // 2, 280), tagline, font=_ugly_font(22), fill=(102, 0, 0),
           anchor="mm")

    blurb_lines = _wrap(blurb, _ugly_font(20), W - 140, d)
    for i, line in enumerate(blurb_lines):
        d.text((W // 2, 340 + i * 30), line, font=_ugly_font(20),
               fill=(0, 0, 0), anchor="mm")

    table_y = 340 + len(blurb_lines) * 30 + 50
    table_h = 320
    d.rectangle((40, table_y, W - 40, table_y + table_h),
                outline=(0, 0, 0), width=3, fill=(255, 255, 255))
    d.line((W // 2, table_y, W // 2, table_y + table_h),
           fill=(0, 0, 0), width=3)
    d.line((40, table_y + 60, W - 40, table_y + 60),
           fill=(0, 0, 0), width=3)
    d.rectangle((40, table_y, W - 40, table_y + 60), fill=(204, 204, 204))
    d.text((W * 0.27, table_y + 30), "OUR PRODUCTS",
           font=_ugly_font(22, bold=True), fill=(0, 0, 0), anchor="mm")
    d.text((W * 0.73, table_y + 30), "CONTACT INFO",
           font=_ugly_font(22, bold=True), fill=(0, 0, 0), anchor="mm")

    products = ["• Item One", "• Item Two", "• Item Three", "• Special!"]
    for i, p in enumerate(products):
        d.text((80, table_y + 90 + i * 40), p, font=_ugly_font(20),
               fill=(0, 0, 180))
    info = [
        f"Phone: 555-{brand[:3].upper()}-2020",
        f"Email: info@{brand.lower()}.com",
        "Hours: Mon-Fri 9-5",
        "Est. 1998",
    ]
    for i, line in enumerate(info):
        d.text((W // 2 + 40, table_y + 90 + i * 40), line,
               font=_ugly_font(18), fill=(0, 0, 0))

    btn_y = table_y + table_h + 60
    btn_w, btn_h = 360, 80
    btn_x = (W - btn_w) // 2
    d.rectangle((btn_x, btn_y, btn_x + btn_w, btn_y + btn_h),
                fill=(255, 0, 0), outline=(0, 0, 0), width=4)
    d.rectangle((btn_x + 4, btn_y + 4, btn_x + btn_w - 4, btn_y + btn_h - 4),
                outline=(255, 255, 0), width=2)
    d.text((btn_x + btn_w // 2, btn_y + btn_h // 2),
           ">>> CLICK HERE NOW <<<",
           font=_ugly_font(24, bold=True), fill=(255, 255, 0), anchor="mm")

    foot_y = H - 80
    d.rectangle((0, foot_y, W, H), fill=(0, 102, 204))
    d.text((W // 2, foot_y + 25),
           f"© 1998-2008 {brand}. All rights reserved.",
           font=_ugly_font(16), fill=(255, 255, 255), anchor="mm")
    d.text((W // 2, foot_y + 52),
           "Best viewed in Internet Explorer 6 at 800x600",
           font=_ugly_font(14), fill=(255, 255, 0), anchor="mm")

    bg.save(path, optimize=True)
    return path


def make_ugly_section(path: Path, *, brand: str) -> Path:
    """A second slide of the bad site: animated-feel testimonial / sidebar."""
    W, H = 1080, 1400
    bg = Image.new("RGB", (W, H), (204, 255, 204))
    d = ImageDraw.Draw(bg)

    d.rectangle((0, 0, W, 80), fill=(153, 0, 153))
    d.text((W // 2, 40), "*** WHAT OUR CUSTOMERS SAY ***",
           font=_ugly_font(26, bold=True), fill=(255, 255, 0), anchor="mm")

    quotes = [
        ('"Best service ever! 5 stars!!!"', "— John D., Verified Buyer"),
        ('"Would buy again and again!!!"', "— Sarah M., New York"),
        ('"This product changed my life!"', "— Mike T., California"),
    ]
    y = 140
    for q, attr in quotes:
        d.rectangle((40, y, W - 40, y + 180), fill=(255, 255, 255),
                    outline=(0, 0, 0), width=2)
        for j in range(5):
            d.text((60 + j * 32, y + 24), "★",
                   font=_ugly_font(36, bold=True), fill=(255, 200, 0))
        d.text((60, y + 80), q, font=_ugly_font(22, serif=True),
               fill=(0, 0, 102))
        d.text((60, y + 130), attr, font=_ugly_font(16),
               fill=(80, 80, 80))
        y += 210

    nl_y = y + 30
    d.rectangle((40, nl_y, W - 40, nl_y + 240), fill=(255, 255, 0),
                outline=(255, 0, 0), width=4)
    d.text((W // 2, nl_y + 40), "!! SIGN UP FOR OUR NEWSLETTER !!",
           font=_ugly_font(24, bold=True), fill=(204, 0, 0), anchor="mm")
    d.text((W // 2, nl_y + 80), "Get 10% off your first order!",
           font=_ugly_font(18), fill=(0, 0, 0), anchor="mm")
    d.rectangle((100, nl_y + 130, 700, nl_y + 180),
                fill=(255, 255, 255), outline=(0, 0, 0), width=2)
    d.text((116, nl_y + 145), "your.email@example.com",
           font=_ugly_font(18), fill=(150, 150, 150))
    d.rectangle((720, nl_y + 130, 980, nl_y + 180),
                fill=(0, 153, 0), outline=(0, 0, 0), width=2)
    d.text((850, nl_y + 155), "SUBSCRIBE!",
           font=_ugly_font(20, bold=True), fill=(255, 255, 0), anchor="mm")

    foot_y = H - 80
    d.rectangle((0, foot_y, W, H), fill=(153, 0, 153))
    d.text((W // 2, foot_y + 25),
           f"Visit our sister sites: {brand}News.com | {brand}Blog.com",
           font=_ugly_font(15), fill=(255, 255, 255), anchor="mm")
    d.text((W // 2, foot_y + 52), "Last updated: April 14, 2008",
           font=_ugly_font(14), fill=(255, 255, 0), anchor="mm")

    bg.save(path, optimize=True)
    return path


def make_ugly_site(out_dir: Path, *, brand: str,
                  tagline: str = "Your one-stop online destination.",
                  blurb: str = ("We are a family owned business with years "
                                "of experience serving customers worldwide. "
                                "Click below to see our amazing products!"),
                  ) -> list[Path]:
    """Generate a deliberately bad-looking site for BEFORE slots."""
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = [
        make_ugly_hero(out_dir / "before-01-home.png", brand=brand,
                       tagline=tagline, blurb=blurb),
        make_ugly_section(out_dir / "before-02-testimonials.png",
                          brand=brand),
    ]
    return paths
