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
    """A homepage that's just generic and boring — mid-2010s template feel.
    Plain white, sans-serif, navy-blue nav, washed-out stock-photo hero,
    centered headline, basic 3-up feature row. Functional, forgettable."""
    W, H = 1080, 1400
    bg = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(bg)

    # Top bar — thin, plain
    d.rectangle((0, 0, W, 80), fill=(255, 255, 255))
    d.line((0, 80, W, 80), fill=(225, 228, 232), width=1)
    d.text((40, 40), brand,
           font=_font(26, bold=True), fill=(33, 53, 92), anchor="lm")
    nav = ["Home", "About", "Services", "Pricing", "Contact"]
    x = W - 40
    for label in reversed(nav):
        tw = d.textbbox((0, 0), label, font=_font(15))[2]
        x -= tw + 32
        d.text((x, 40), label, font=_font(15), fill=(85, 95, 110), anchor="lm")

    # Hero band — washed greyscale "stock photo" gradient
    hero_top, hero_bot = 80, 700
    hero = _grad((W, hero_bot - hero_top), (88, 100, 118), (140, 152, 168))
    bg.paste(hero, (0, hero_top))
    d = ImageDraw.Draw(bg)
    # darken overlay strip behind text
    overlay = Image.new("RGBA", (W, 240), (10, 14, 22, 90))
    bg.paste(overlay, (0, hero_top + 200), overlay)
    d = ImageDraw.Draw(bg)

    d.text((W // 2, hero_top + 280),
           f"Welcome to {brand}",
           font=_font(54, bold=True), fill=(255, 255, 255), anchor="mm")
    d.text((W // 2, hero_top + 350), tagline,
           font=_font(20), fill=(225, 230, 238), anchor="mm")

    # Plain pill CTA
    cta_y = hero_top + 410
    cta_w, cta_h = 200, 52
    cta_x = (W - cta_w) // 2
    d.rounded_rectangle((cta_x, cta_y, cta_x + cta_w, cta_y + cta_h),
                        radius=3, fill=(33, 110, 200))
    d.text((cta_x + cta_w // 2, cta_y + cta_h // 2), "Learn More",
           font=_font(16, bold=True), fill=(255, 255, 255), anchor="mm")

    # Intro paragraph
    blurb_y = 740
    blurb_lines = _wrap(blurb, _font(17), int(W * 0.62), d)
    for i, line in enumerate(blurb_lines):
        d.text((W // 2, blurb_y + i * 26), line,
               font=_font(17), fill=(85, 95, 110), anchor="mm")

    # Three-up feature grid — plain cards with rounded greyscale icons
    feat_y = blurb_y + len(blurb_lines) * 26 + 50
    titles = [
        ("Quality Service", "Committed to excellence in every interaction."),
        ("Trusted Experts", "Decades of combined industry experience."),
        ("Customer First", "Your satisfaction is our top priority."),
    ]
    col_w = (W - 80 - 40) // 3
    for i, (t, s) in enumerate(titles):
        cx = 40 + i * (col_w + 20)
        # icon disk
        d.ellipse((cx + col_w // 2 - 28, feat_y, cx + col_w // 2 + 28,
                   feat_y + 56), fill=(238, 242, 246))
        d.ellipse((cx + col_w // 2 - 10, feat_y + 18,
                   cx + col_w // 2 + 10, feat_y + 38),
                  fill=(150, 165, 185))
        d.text((cx + col_w // 2, feat_y + 86), t,
               font=_font(18, bold=True), fill=(45, 55, 70), anchor="mm")
        for j, line in enumerate(_wrap(s, _font(14), col_w - 20, d)):
            d.text((cx + col_w // 2, feat_y + 116 + j * 20), line,
                   font=_font(14), fill=(120, 130, 145), anchor="mm")

    # Footer bar — plain dark navy
    foot_y = H - 80
    d.rectangle((0, foot_y, W, H), fill=(33, 45, 65))
    d.text((40, foot_y + 30), brand,
           font=_font(16, bold=True), fill=(255, 255, 255))
    d.text((40, foot_y + 54), f"© 2018 {brand}. All rights reserved.",
           font=_font(12), fill=(160, 170, 185))
    foot_links = ["Privacy", "Terms", "Sitemap"]
    fx = W - 40
    for label in reversed(foot_links):
        tw = d.textbbox((0, 0), label, font=_font(13))[2]
        fx -= tw + 24
        d.text((fx, foot_y + 40), label, font=_font(13),
               fill=(190, 200, 215), anchor="lm")

    bg.save(path, optimize=True)
    return path


def make_ugly_section(path: Path, *, brand: str) -> Path:
    """Second BEFORE slide: a plain about/testimonials section.
    Generic stock-template feel — light grey blocks, lorem-ish copy."""
    W, H = 1080, 1400
    bg = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(bg)

    # Section title
    d.text((W // 2, 100), "About Us",
           font=_font(36, bold=True), fill=(45, 55, 70), anchor="mm")
    d.text((W // 2, 144), "Get to know who we are and what we stand for.",
           font=_font(16), fill=(120, 130, 145), anchor="mm")

    # Two-col split: greyscale image block + copy
    split_y = 200
    img_w = (W - 80 - 40) // 2
    d.rectangle((40, split_y, 40 + img_w, split_y + 380),
                fill=(235, 240, 246))
    # tiny "image" mountains
    d.polygon([(70, split_y + 320), (160, split_y + 200),
               (240, split_y + 280), (340, split_y + 160),
               (40 + img_w - 20, split_y + 310),
               (40 + img_w - 20, split_y + 380),
               (70, split_y + 380)], fill=(190, 200, 215))
    d.ellipse((40 + img_w - 120, split_y + 60,
               40 + img_w - 60, split_y + 120), fill=(220, 225, 232))

    copy_x = 40 + img_w + 40
    d.text((copy_x, split_y + 20), "Our Story",
           font=_font(22, bold=True), fill=(45, 55, 70))
    body = (
        f"At {brand}, we believe in delivering quality and value to every "
        f"customer. Founded with a simple goal — to make great service "
        f"accessible — we've been proudly serving our community for over "
        f"a decade. Our dedicated team works hard every day to exceed your "
        f"expectations."
    )
    for i, line in enumerate(_wrap(body, _font(15), W - copy_x - 60, d)):
        d.text((copy_x, split_y + 70 + i * 24), line,
               font=_font(15), fill=(95, 105, 120))

    btn_y2 = split_y + 320
    d.rounded_rectangle((copy_x, btn_y2, copy_x + 140, btn_y2 + 40),
                        radius=3, fill=(33, 110, 200))
    d.text((copy_x + 70, btn_y2 + 20), "Read More",
           font=_font(14, bold=True), fill=(255, 255, 255), anchor="mm")

    # Testimonial strip — light grey background, two plain cards
    ts_y = 640
    d.rectangle((0, ts_y, W, ts_y + 480), fill=(247, 249, 252))
    d.text((W // 2, ts_y + 50), "What Our Clients Say",
           font=_font(26, bold=True), fill=(45, 55, 70), anchor="mm")
    quotes = [
        ('"Great service and friendly staff. Would recommend."',
         "John Smith"),
        ('"Professional, on time, and exactly what we needed."',
         "Sarah Johnson"),
    ]
    card_w = (W - 80 - 30) // 2
    for i, (q, n) in enumerate(quotes):
        cx = 40 + i * (card_w + 30)
        cy = ts_y + 110
        d.rounded_rectangle((cx, cy, cx + card_w, cy + 280),
                            radius=4, fill=(255, 255, 255))
        d.line((cx, cy, cx + card_w, cy), fill=(230, 234, 240), width=1)
        for s in range(5):
            d.text((cx + 24 + s * 22, cy + 28), "★",
                   font=_font(18), fill=(255, 195, 60))
        for j, line in enumerate(_wrap(q, _font(15), card_w - 48, d)):
            d.text((cx + 24, cy + 80 + j * 24), line,
                   font=_font(15), fill=(75, 85, 100))
        d.line((cx + 24, cy + 210, cx + 80, cy + 210),
               fill=(200, 208, 220), width=2)
        d.text((cx + 24, cy + 230), n,
               font=_font(13, bold=True), fill=(95, 105, 120))

    # Footer
    foot_y = H - 80
    d.rectangle((0, foot_y, W, H), fill=(33, 45, 65))
    d.text((40, foot_y + 30), brand,
           font=_font(16, bold=True), fill=(255, 255, 255))
    d.text((40, foot_y + 54), f"© 2018 {brand}. All rights reserved.",
           font=_font(12), fill=(160, 170, 185))

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
