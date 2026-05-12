"""One-off render for the Sable carousel.

Style brief from user:
  - Smooth clean minimal background (NEW palette — warm oat, distinct from
    the cream used in earlier carousels).
  - Engaging fonts (Inter Bold for hook, Inter Regular for subhead).
  - Strong drop shadow on every screenshot so they "stand out" off the bg.
  - Slide 1: strong hook (headline + subhead) at top, screenshot below.
  - Slides 2..N: screenshot centered, slide counter top-right.

The fullpage stitched screenshot isn't on disk yet, so this renders the
4 section shots already in screenshots/sable-restaurant/.
"""
from __future__ import annotations
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

os.environ.setdefault("LOVEABLE_UGC_DIR", "C:/Users/Jack/Desktop/Loveable-UGC")

OUTPUT_ROOT = Path(os.environ["LOVEABLE_UGC_DIR"])
SCREENSHOTS_DIR = OUTPUT_ROOT / "screenshots" / "sable-restaurant"
OUT_DIR = OUTPUT_ROOT / "carousels" / "sable-restaurant-01"

# ------------------------------------------------------- palette (warm oat)
BG = (231, 224, 209)          # warm oat — clean minimal
INK = (28, 25, 22)            # deep warm-black headline
MUTED = (130, 120, 110)       # warm grey subhead / slide counter

# --------------------------------------------------------- fonts
WIN_FONTS = Path("C:/Windows/Fonts")
FONT_BOLD = str(WIN_FONTS / "Inter-Bold-slnt=0.ttf")
FONT_REG = str(WIN_FONTS / "Inter-Regular-slnt=0.ttf")
# Hook font: Inter Medium — one weight up from Regular, shipped in
# repo assets/ so we don't depend on it being system-installed.
FONT_MEDIUM = str(Path(__file__).parent.parent / "assets" / "Inter-Medium.ttf")
FONT_HOOK = FONT_MEDIUM

# Lovable wordmark icon (heart). Pasted at the end of the hook headline.
LOVABLE_LOGO = Path(__file__).parent.parent / "assets" / "lovable-icon.png"

# Real-life photo background for the slide-1 variant.
BG_PHOTO = Path(__file__).parent.parent / "assets" / "bg-photo-01.jpg"

SIZE_9X16 = (1080, 1920)
SIZE_1X1 = (1080, 1080)
# 2x output sizes — same designs rendered natively at double resolution.
# Use these as the high-quality archive / print version. PIL renders text,
# shapes, screenshots and shadows at full resolution at this size, so they
# stay crisp. (The photo background softens slightly due to source
# resolution limits, but everything Claude draws stays sharp.)
SIZE_9X16_2X = (2160, 3840)
SIZE_1X1_2X = (2160, 2160)

HOOK_HEADLINE = "POV: I built this website on lovable in 2 days"
HOOK_SUBHEAD = ""


def _make_background(size: tuple[int, int]) -> Image.Image:
    """Warm-oat background with subtle radial vignette, film grain, and a
    thin editorial hairline near the top edge.

    Goal: keep the minimal feel of the original flat bg, but add enough
    micro-texture and structure that the slide doesn't read as a default
    PowerPoint export.
    """
    W, H = size
    canvas = Image.new("RGB", size, BG).convert("RGBA")

    # --- radial vignette: light at center, ~10 units darker at corners ---
    small = 320
    rg = Image.new("L", (small, small), 0)
    rd = ImageDraw.Draw(rg)
    for r in range(small // 2, 0, -1):
        v = int(255 * (1 - r / (small / 2)) ** 1.4)
        rd.ellipse((small / 2 - r, small / 2 - r,
                    small / 2 + r, small / 2 + r), fill=v)
    rg = rg.resize(size, Image.BICUBIC).filter(ImageFilter.GaussianBlur(40))
    darker = Image.new("RGBA", size,
                       (max(0, BG[0] - 14), max(0, BG[1] - 14),
                        max(0, BG[2] - 12), 255))
    canvas = Image.composite(canvas, darker, rg)

    # --- film-grain noise overlay (warm tone) ---
    noise = Image.effect_noise(size, 22).convert("L")
    # Map gray midpoint to a low-alpha mask so grain reads as subtle texture.
    alpha = noise.point(lambda v: max(0, min(22, int(abs(v - 128) * 0.18))))
    grain_color = Image.new("RGBA", size, (60, 48, 36, 0))
    grain_color.putalpha(alpha)
    canvas = Image.alpha_composite(canvas, grain_color)

    # --- editorial hairlines top + bottom, very faint ---
    d = ImageDraw.Draw(canvas)
    hair = (BG[0] - 30, BG[1] - 32, BG[2] - 34, 90)
    shape = (BG[0] - 36, BG[1] - 38, BG[2] - 40, 75)
    pad_x = int(W * 0.07)
    y_top = int(H * 0.035)
    y_bot = H - int(H * 0.035)
    d.line((pad_x, y_top, W - pad_x, y_top), fill=hair, width=1)
    d.line((pad_x, y_bot, W - pad_x, y_bot), fill=hair, width=1)

    # --- minimalistic geometric shapes scattered as background detail ---
    # Positions are percentage-based so they scale to either ratio.
    def _pct(px, py):
        return (int(W * px), int(H * py))

    # Outlined circle, lower-left
    r1 = int(W * 0.055)
    cx1, cy1 = _pct(0.13, 0.82)
    d.ellipse((cx1 - r1, cy1 - r1, cx1 + r1, cy1 + r1),
              outline=shape, width=2)

    # Smaller outlined circle, upper-right
    r2 = int(W * 0.04)
    cx2, cy2 = _pct(0.88, 0.18)
    d.ellipse((cx2 - r2, cy2 - r2, cx2 + r2, cy2 + r2),
              outline=shape, width=2)

    # Small filled dot, mid-right
    r3 = int(W * 0.008)
    cx3, cy3 = _pct(0.91, 0.55)
    d.ellipse((cx3 - r3, cy3 - r3, cx3 + r3, cy3 + r3),
              fill=(shape[0], shape[1], shape[2], 140))

    # Plus-mark, lower-right
    cx4, cy4 = _pct(0.82, 0.91)
    arm = int(W * 0.018)
    d.line((cx4 - arm, cy4, cx4 + arm, cy4), fill=shape, width=2)
    d.line((cx4, cy4 - arm, cx4, cy4 + arm), fill=shape, width=2)

    # Plus-mark, upper-left under the brand mark
    cx5, cy5 = _pct(0.09, 0.27)
    arm2 = int(W * 0.014)
    d.line((cx5 - arm2, cy5, cx5 + arm2, cy5), fill=shape, width=2)
    d.line((cx5, cy5 - arm2, cx5, cy5 + arm2), fill=shape, width=2)

    # Thin short diagonal stroke, mid-left
    sx, sy = _pct(0.06, 0.55)
    length = int(W * 0.035)
    d.line((sx, sy + length, sx + length, sy), fill=shape, width=2)

    # --- tiny brand mark top-left ---
    tiny = _font(FONT_REG, max(14, int(W * 0.018)))
    mark = "SABLE  \u2014  N\u00b0 01"
    d.text((pad_x, y_top - max(14, int(W * 0.018)) - 8),
           mark, font=tiny, fill=(MUTED[0], MUTED[1], MUTED[2], 220))

    return canvas.convert("RGB")


def _font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def _wrap(text: str, fnt, max_w: int, d: ImageDraw.ImageDraw) -> list[str]:
    out: list[str] = []
    for para in text.split("\n"):
        line: list[str] = []
        for w in para.split(" "):
            test = " ".join(line + [w])
            bb = d.textbbox((0, 0), test, font=fnt)
            if bb[2] - bb[0] > max_w and line:
                out.append(" ".join(line))
                line = [w]
            else:
                line.append(w)
        if line:
            out.append(" ".join(line))
    return out


def _paste_screenshot_with_shadow(canvas: Image.Image, shot: Image.Image,
                                  box: tuple[int, int, int, int],
                                  radius: int = 24,
                                  shadow_strength: int = 110,
                                  shadow_blur: int = 32,
                                  shadow_offset_y: int = 24) -> None:
    """Fit shot inside box, rounded corners, prominent drop shadow."""
    x1, y1, x2, y2 = box
    max_w = x2 - x1
    max_h = y2 - y1

    sw, sh = shot.size
    scale = min(max_w / sw, max_h / sh)
    new_w = int(sw * scale)
    new_h = int(sh * scale)
    resized = shot.resize((new_w, new_h), Image.LANCZOS)

    mask = Image.new("L", (new_w, new_h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, new_w, new_h),
                                           radius=radius, fill=255)
    rounded = Image.new("RGBA", (new_w, new_h), (0, 0, 0, 0))
    rounded.paste(resized.convert("RGBA"), (0, 0), mask)

    pad = shadow_blur * 3
    shadow = Image.new("RGBA", (new_w + pad * 2, new_h + pad * 2),
                       (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        (pad, pad, pad + new_w, pad + new_h),
        radius=radius, fill=(0, 0, 0, shadow_strength),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(shadow_blur))

    cx = x1 + (max_w - new_w) // 2
    cy = y1 + (max_h - new_h) // 2

    canvas.paste(shadow, (cx - pad, cy - pad + shadow_offset_y), shadow)
    canvas.paste(rounded, (cx, cy), rounded)


def _paste_fullpage_top_anchored(canvas: Image.Image, shot: Image.Image,
                                  box: tuple[int, int, int, int],
                                  radius: int = 24,
                                  shadow_strength: int = 130,
                                  shadow_blur: int = 36,
                                  visible_fraction: float = 0.5) -> None:
    """Slide-1 fullpage treatment.

    Scale the fullpage screenshot DOWN so that ``visible_fraction`` of its
    full height fits inside the visible canvas box, then anchor it to the
    top of the box (the rest still hangs off the bottom). Centered
    horizontally inside the box so the surrounding warm-oat margin reads
    as deliberate framing.
    """
    x1, y1, x2, y2 = box
    box_w = x2 - x1
    visible_h = y2 - y1
    sw, sh = shot.size

    # Scale by HEIGHT so the visible portion of the page = visible_fraction
    # of the entire page. (visible_h / new_h == visible_fraction)
    target_h = visible_h / visible_fraction
    scale = target_h / sh
    # Don't let the image exceed the box width.
    max_scale_w = box_w / sw
    scale = min(scale, max_scale_w)

    new_w = int(sw * scale)
    new_h = int(sh * scale)
    resized = shot.resize((new_w, new_h), Image.LANCZOS)

    # Rounded corners only on the visible top corners — bottom is cut off
    # by the canvas, so rounding it would do nothing.
    mask = Image.new("L", (new_w, new_h), 255)
    md = ImageDraw.Draw(mask)
    # mask only the top two corners
    md.rectangle((0, 0, radius, radius), fill=0)
    md.rectangle((new_w - radius, 0, new_w, radius), fill=0)
    md.pieslice((0, 0, radius * 2, radius * 2), 180, 270, fill=255)
    md.pieslice((new_w - radius * 2, 0, new_w, radius * 2), 270, 360, fill=255)
    rounded = Image.new("RGBA", (new_w, new_h), (0, 0, 0, 0))
    rounded.paste(resized.convert("RGBA"), (0, 0), mask)

    # Shadow — soft, only behind the visible top portion (the rest of the
    # image overflows the canvas anyway).
    shadow_h = min(new_h, visible_h)
    pad = shadow_blur * 3
    shadow = Image.new("RGBA", (new_w + pad * 2, shadow_h + pad * 2),
                       (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        (pad, pad, pad + new_w, pad + shadow_h),
        radius=radius, fill=(0, 0, 0, shadow_strength),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(shadow_blur))

    # Centered horizontally inside the box.
    cx = x1 + (box_w - new_w) // 2
    cy = y1
    canvas.paste(shadow, (cx - pad, cy - pad + 18), shadow)
    canvas.paste(rounded, (cx, cy), rounded)


def _draw_hook(canvas: Image.Image, headline: str, subhead: str) -> None:
    """Slide-1 hook: Inter Regular, centered. The Lovable heart logo is
    pasted at the end of the last line, slightly larger than the cap
    height and optically centered to the line's visible bounds.

    On 9:16 (TikTok) the hook is forced to two lines:
        "I built this website"
        "on lovable in 2 days [logo]"
    On 1:1 (square) the font size is reduced and the line wraps freely.
    """
    W, H = canvas.size
    d = ImageDraw.Draw(canvas)

    is_tall = H > W * 1.2  # True for 9:16, False for 1:1

    pad_x = int(W * 0.085)
    pad_top = int(H * 0.115)

    if is_tall:
        lines = ["POV: I built this website", "on lovable in 2 days"]
        size = int(W * 0.058)  # bumped slightly per user's brief
    else:
        # Reduced quite a bit per the user's brief.
        size = int(W * 0.034)
        # Wrap freely after reserving room for the trailing logo.
        max_text_w = W - pad_x * 2
        fnt_tmp = _font(FONT_HOOK, size)
        logo_reserve_tmp = int(size * 1.25) + int(size * 0.35)
        # Simple two-line break: split into halves.
        lines = _wrap(headline, fnt_tmp, max_text_w - logo_reserve_tmp, d)
        if len(lines) > 2:
            # Force two lines: rejoin and split at midpoint word.
            words = headline.split()
            mid = len(words) // 2
            lines = [" ".join(words[:mid]), " ".join(words[mid:])]

    fnt = _font(FONT_HOOK, size)

    # Logo: slightly larger than before (was 0.95 of cap height, now 1.25)
    # and aligned to the actual visible vertical center of the last line.
    logo = Image.open(LOVABLE_LOGO).convert("RGBA")
    logo_h = int(size * 1.25)
    lw, lh = logo.size
    logo_w = int(lw * (logo_h / lh))
    logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
    gap = int(size * 0.32)

    bb_metrics = d.textbbox((0, 0), "Mg", font=fnt)
    line_h = int((bb_metrics[3] - bb_metrics[1]) * 1.25)

    stroke_w = max(2, int(size * 0.08))
    stroke_fill = (255, 255, 255)

    y = pad_top
    for i, ln in enumerate(lines):
        is_last = (i == len(lines) - 1)
        if is_last:
            text_w = d.textbbox((0, 0), ln, font=fnt,
                                stroke_width=stroke_w)[2]
            combined_w = text_w + gap + logo_w
            start_x = (W - combined_w) // 2
            d.text((start_x, y), ln, font=fnt, fill=INK, anchor="la",
                   stroke_width=stroke_w, stroke_fill=stroke_fill)
            visible_bb = d.textbbox((start_x, y), ln, font=fnt,
                                    anchor="la", stroke_width=stroke_w)
            line_center_y = (visible_bb[1] + visible_bb[3]) // 2
            logo_y = line_center_y - logo_h // 2
            canvas.paste(logo, (start_x + text_w + gap, logo_y), logo)
        else:
            d.text((W // 2, y), ln, font=fnt, fill=INK, anchor="ma",
                   stroke_width=stroke_w, stroke_fill=stroke_fill)
        y += line_h

    if subhead:
        sub_fnt = _font(FONT_REG, int(size * 0.5))
        y += int(line_h * 0.25)
        d.text((W // 2, y), subhead, font=sub_fnt, fill=MUTED, anchor="ma")


def _draw_slide_counter(canvas: Image.Image, n: int, total: int) -> None:
    W, H = canvas.size
    d = ImageDraw.Draw(canvas)
    fnt = _font(FONT_REG, int(W * 0.026))
    text = f"{n} / {total}"
    pad = int(W * 0.06)
    d.text((W - pad, pad), text, font=fnt, fill=MUTED, anchor="rs")


def _cover_fit(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Scale + center-crop ``img`` to exactly ``size`` (CSS object-fit:cover)."""
    tw, th = size
    iw, ih = img.size
    scale = max(tw / iw, th / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    resized = img.resize((nw, nh), Image.LANCZOS)
    x = (nw - tw) // 2
    y = (nh - th) // 2
    return resized.crop((x, y, x + tw, y + th))


def _draw_hook_on_photo(canvas: Image.Image) -> None:
    """Slide-1 photo variant hook: white text with a soft dark drop shadow
    for legibility over a photographic background. Same lines/sizes/logo
    as the regular hook."""
    W, H = canvas.size
    is_tall = H > W * 1.2

    pad_x = int(W * 0.085)
    pad_top = int(H * 0.115)

    if is_tall:
        lines = ["POV: I built this website", "on lovable in 2 days"]
        size = int(W * 0.058)
    else:
        size = int(W * 0.034)
        d_tmp = ImageDraw.Draw(canvas)
        max_text_w = W - pad_x * 2
        fnt_tmp = _font(FONT_HOOK, size)
        logo_reserve_tmp = int(size * 1.25) + int(size * 0.35)
        lines = _wrap(HOOK_HEADLINE, fnt_tmp,
                      max_text_w - logo_reserve_tmp, d_tmp)
        if len(lines) > 2:
            words = HOOK_HEADLINE.split()
            mid = len(words) // 2
            lines = [" ".join(words[:mid]), " ".join(words[mid:])]

    fnt = _font(FONT_HOOK, size)

    logo = Image.open(LOVABLE_LOGO).convert("RGBA")
    logo_h = int(size * 1.25)
    lw, lh = logo.size
    logo_w = int(lw * (logo_h / lh))
    logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
    gap = int(size * 0.32)

    bb_metrics = ImageDraw.Draw(canvas).textbbox((0, 0), "Mg", font=fnt)
    line_h = int((bb_metrics[3] - bb_metrics[1]) * 1.25)

    text_fill = (255, 255, 255)
    shadow_fill = (0, 0, 0, 160)
    shadow_offset = max(2, int(size * 0.06))
    shadow_blur = max(6, int(size * 0.25))

    # Render text + shadows on a transparent overlay, then composite onto
    # the canvas. This gives us a soft gaussian shadow under each line.
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    shadow_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    sd = ImageDraw.Draw(shadow_layer)

    y = pad_top
    last_logo_pos = None
    for i, ln in enumerate(lines):
        is_last = (i == len(lines) - 1)
        if is_last:
            text_w = od.textbbox((0, 0), ln, font=fnt)[2]
            combined_w = text_w + gap + logo_w
            start_x = (W - combined_w) // 2
            sd.text((start_x + shadow_offset, y + shadow_offset),
                    ln, font=fnt, fill=shadow_fill, anchor="la")
            od.text((start_x, y), ln, font=fnt, fill=text_fill,
                    anchor="la")
            visible_bb = od.textbbox((start_x, y), ln, font=fnt,
                                     anchor="la")
            line_center_y = (visible_bb[1] + visible_bb[3]) // 2
            logo_y = line_center_y - logo_h // 2
            last_logo_pos = (start_x + text_w + gap, logo_y)
        else:
            sd.text((W // 2 + shadow_offset, y + shadow_offset),
                    ln, font=fnt, fill=shadow_fill, anchor="ma")
            od.text((W // 2, y), ln, font=fnt, fill=text_fill,
                    anchor="ma")
        y += line_h

    # Blur the shadow layer and composite shadow → text → logo.
    shadow_layer = shadow_layer.filter(
        ImageFilter.GaussianBlur(shadow_blur))
    base = canvas.convert("RGBA")
    base = Image.alpha_composite(base, shadow_layer)
    base = Image.alpha_composite(base, overlay)
    if last_logo_pos is not None:
        base.paste(logo, last_logo_pos, logo)
    # Copy back into the original canvas.
    canvas.paste(base.convert("RGB"))


def render_slide_01_photo(size: tuple[int, int]) -> Image.Image:
    """Slide-1 variant: real-life moody restaurant photo, slightly darkened,
    with the POV hook and Lovable logo overlaid on top."""
    W, H = size

    # 1. Photo, cover-fit to canvas.
    photo = Image.open(BG_PHOTO).convert("RGB")
    canvas = _cover_fit(photo, (W, H))

    # 2. Slight uniform darken (alpha 70/255 ~ 27%).
    darken = Image.new("RGBA", (W, H), (0, 0, 0, 70))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), darken).convert("RGB")

    # 3. Soft gradient at the top for extra text legibility — barely there
    #    (top alpha 90, fades to 0 over the upper third).
    grad = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    grad_h = int(H * 0.42)
    for i in range(grad_h):
        a = int(90 * (1 - i / grad_h) ** 1.3)
        ImageDraw.Draw(grad).line((0, i, W, i), fill=(0, 0, 0, a))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), grad).convert("RGB")

    # 4. Hook with white text + drop shadow.
    _draw_hook_on_photo(canvas)

    # 5. Slide counter in light grey.
    d = ImageDraw.Draw(canvas)
    cnt_fnt = _font(FONT_REG, int(W * 0.026))
    pad = int(W * 0.06)
    d.text((W - pad, pad), "1 / 5", font=cnt_fnt,
           fill=(230, 226, 218), anchor="rs")

    return canvas


def render_slide(size, shot_path: Path, *, is_first: bool,
                  slide_num: int, total: int) -> Image.Image:
    W, H = size
    canvas = _make_background(size)

    pad = int(W * 0.07)

    shot = Image.open(shot_path).convert("RGB")

    if is_first:
        # Hook sits lower on the canvas; image enlarged (was visible 0.5 of
        # full page, now 0.38) but still hangs off bottom.
        top_block_h = int(H * 0.24)
        box = (pad, top_block_h, W - pad, H)
        _draw_hook(canvas, HOOK_HEADLINE, HOOK_SUBHEAD)
        _paste_fullpage_top_anchored(canvas, shot, box,
                                     visible_fraction=0.38)
    else:
        box = (pad, int(H * 0.08), W - pad, H - pad)
        _paste_screenshot_with_shadow(canvas, shot, box)

    _draw_slide_counter(canvas, slide_num, total)

    return canvas


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Slides in order. 01-fullpage gets bottom-hang treatment (slide 1).
    slides: list[Path] = []
    for name in ["01-fullpage.png", "02-hero.png", "03-kitchen.png",
                 "04-lookbook.png", "05-footer.png"]:
        p = SCREENSHOTS_DIR / name
        if p.exists():
            slides.append(p)

    total = len(slides)
    print(f"rendering {total} slides from:")
    for s in slides:
        print(f"  - {s.name}")

    targets = [
        (SIZE_9X16,    "1080x1920"),
        (SIZE_1X1,     "1080x1080"),
        (SIZE_9X16_2X, "2160x3840"),  # high-quality 2x archive
        (SIZE_1X1_2X,  "2160x2160"),  # high-quality 2x archive
    ]

    for (W, H), label in targets:
        ratio_dir = OUT_DIR / label
        ratio_dir.mkdir(parents=True, exist_ok=True)
        for i, shot in enumerate(slides, start=1):
            img = render_slide((W, H), shot, is_first=(i == 1),
                               slide_num=i, total=total)
            png_path = ratio_dir / f"slide-{i:02d}.png"
            jpg_path = ratio_dir / f"slide-{i:02d}.jpg"
            img.save(png_path, optimize=True)
            img.save(jpg_path, quality=95, subsampling=0,
                     progressive=True)
            print(f"  wrote {png_path}")

        # Photo-bg variant of slide 1.
        variant = render_slide_01_photo((W, H))
        png_path = ratio_dir / "slide-01-photo.png"
        jpg_path = ratio_dir / "slide-01-photo.jpg"
        variant.save(png_path, optimize=True)
        variant.save(jpg_path, quality=95, subsampling=0,
                     progressive=True)
        print(f"  wrote {png_path}")

    print(f"\nDONE: carousel at {OUT_DIR}")


if __name__ == "__main__":
    main()
