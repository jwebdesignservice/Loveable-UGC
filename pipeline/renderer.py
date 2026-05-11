"""Slide renderer. Site-first, centered layout matching the
fastlaunchmvp template.

  slide 1 : site hero screenshot, hook text overlay in a black pill
  slide 2..N : site screenshot centered on warm bg, no text

Renders each carousel at 1080x1920 (9:16) and 1080x1080 (1:1).
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from .config import (PAPER, INK, MUTED, PILL_BG, PILL_FG,
                     SIZE_9X16, SIZE_1X1, FONT_REG, FONT_BOLD)


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def _wrap(text: str, fnt: ImageFont.FreeTypeFont, max_w: int,
          draw: ImageDraw.ImageDraw) -> list[str]:
    out: list[str] = []
    for para in text.split("\n"):
        line: list[str] = []
        for w in para.split(" "):
            test = " ".join(line + [w])
            bb = draw.textbbox((0, 0), test, font=fnt)
            if bb[2] - bb[0] > max_w and line:
                out.append(" ".join(line))
                line = [w]
            else:
                line.append(w)
        if line:
            out.append(" ".join(line))
    return out


def _paste_centered(canvas: Image.Image, screenshot: Image.Image,
                    box: tuple[int, int, int, int],
                    radius: int = 22) -> None:
    """Fit a screenshot inside box, rounded corners + soft shadow."""
    x1, y1, x2, y2 = box
    max_w = x2 - x1
    max_h = y2 - y1

    sw, sh = screenshot.size
    scale = min(max_w / sw, max_h / sh)
    new_w = int(sw * scale)
    new_h = int(sh * scale)
    resized = screenshot.resize((new_w, new_h), Image.LANCZOS)

    # rounded mask
    mask = Image.new("L", (new_w, new_h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, new_w, new_h),
                                           radius=radius, fill=255)
    rounded = Image.new("RGBA", (new_w, new_h), (0, 0, 0, 0))
    rounded.paste(resized.convert("RGBA"), (0, 0), mask)

    # shadow
    shadow = Image.new("RGBA", (new_w + 80, new_h + 80), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        (40, 40, 40 + new_w, 40 + new_h), radius=radius, fill=(0, 0, 0, 70)
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))

    cx = x1 + (max_w - new_w) // 2
    cy = y1 + (max_h - new_h) // 2

    canvas.paste(shadow, (cx - 40, cy - 32), shadow)
    canvas.paste(rounded, (cx, cy), rounded)


def _draw_hook_pill(canvas: Image.Image, text: str, *,
                    y_center: int, max_text_width: int) -> None:
    d = ImageDraw.Draw(canvas)
    W = canvas.size[0]

    size = int(W * 0.062)
    while size > 36:
        fnt = _font(size, bold=True)
        lines = _wrap(text, fnt, max_text_width, d)
        bb = d.textbbox((0, 0), "Mg", font=fnt)
        line_h = int((bb[3] - bb[1]) * 1.18)
        block_h = line_h * len(lines)
        widest = max(d.textbbox((0, 0), ln, font=fnt)[2] for ln in lines)
        if widest <= max_text_width and block_h <= int(W * 0.4):
            break
        size -= 4
    else:
        fnt = _font(36, bold=True)
        lines = _wrap(text, fnt, max_text_width, d)
        bb = d.textbbox((0, 0), "Mg", font=fnt)
        line_h = int((bb[3] - bb[1]) * 1.18)
        block_h = line_h * len(lines)

    pad_x = int(W * 0.05)
    pad_y = int(W * 0.038)
    widest = max(d.textbbox((0, 0), ln, font=fnt)[2] for ln in lines)
    pill_w = widest + pad_x * 2
    pill_h = block_h + pad_y * 2
    pill_x = (W - pill_w) // 2
    pill_y = y_center - pill_h // 2

    d.rounded_rectangle((pill_x, pill_y, pill_x + pill_w, pill_y + pill_h),
                        radius=int(pill_h * 0.18), fill=PILL_BG)

    ty = pill_y + pad_y
    for ln in lines:
        line_w = d.textbbox((0, 0), ln, font=fnt)[2]
        tx = pill_x + (pill_w - line_w) // 2
        d.text((tx, ty), ln, font=fnt, fill=PILL_FG)
        ty += line_h


def render_slide(size: tuple[int, int], screenshot_path: Path,
                 hook: str | None, slide_num: str | None) -> Image.Image:
    W, H = size
    canvas = Image.new("RGB", size, PAPER)

    pad = int(W * 0.06)

    if hook:
        hook_top = int(H * 0.06)
        hook_band = int(H * 0.22)
        box = (pad, hook_top + hook_band, W - pad, H - pad)
    else:
        box = (pad, pad, W - pad, H - pad)

    if screenshot_path.exists():
        shot = Image.open(screenshot_path).convert("RGB")
        _paste_centered(canvas, shot, box)
    else:
        d = ImageDraw.Draw(canvas)
        d.rounded_rectangle(box, radius=22, fill=(220, 215, 205))
        d.text((box[0] + 30, box[1] + 30),
               f"(missing: {screenshot_path.name})",
               font=_font(28), fill=MUTED)

    if hook:
        _draw_hook_pill(canvas, hook,
                        y_center=int(H * 0.16),
                        max_text_width=int(W * 0.82))

    if slide_num:
        d = ImageDraw.Draw(canvas)
        f = _font(int(W * 0.024))
        d.text((W - pad, H - pad // 2), slide_num,
               font=f, fill=MUTED, anchor="rs")

    return canvas


def render_carousel(*, hook: str, screenshots: list[Path], out_dir: Path,
                    sizes: tuple[tuple[int, int], ...] = (SIZE_9X16, SIZE_1X1)) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    total = len(screenshots)
    written: dict[str, list[str]] = {}

    for (W, H) in sizes:
        ratio_dir = out_dir / f"{W}x{H}"
        ratio_dir.mkdir(exist_ok=True)
        paths: list[str] = []
        for i, shot in enumerate(screenshots, start=1):
            slide_hook = hook if i == 1 else None
            num = f"{i} / {total}"
            img = render_slide((W, H), shot, slide_hook, num)
            p = ratio_dir / f"slide-{i:02d}.png"
            img.save(p, optimize=True)
            paths.append(str(p))
        written[f"{W}x{H}"] = paths

    return written


# ---------------------------------------------------------- comparison render


def _draw_corner_tag(canvas: Image.Image, label: str, *,
                     bg: tuple[int, int, int],
                     fg: tuple[int, int, int]) -> None:
    """Small label in the top-left corner of a slide (BEFORE / AFTER)."""
    W = canvas.size[0]
    d = ImageDraw.Draw(canvas)
    fnt = _font(int(W * 0.035), bold=True)
    pad_x = int(W * 0.035)
    pad_y = int(W * 0.018)
    tb = d.textbbox((0, 0), label, font=fnt)
    tw = tb[2] - tb[0]
    th = tb[3] - tb[1]
    x = int(W * 0.06)
    y = int(W * 0.06)
    d.rounded_rectangle(
        (x, y, x + tw + pad_x * 2, y + th + pad_y * 2),
        radius=int((th + pad_y * 2) * 0.3), fill=bg,
    )
    d.text((x + pad_x, y + pad_y - 2), label, font=fnt, fill=fg)


def render_comparison_slide(size: tuple[int, int], screenshot_path: Path,
                            tag: str | None, tag_color: str | None,
                            slide_num: str | None,
                            hook: str | None) -> Image.Image:
    """A slide for BEFORE/AFTER style carousels.

    `tag` shows in the top-left as a small label. Hook (if given) sits in
    its usual pill at the top — only slide 1 of the carousel has it.
    """
    W, H = size
    img = render_slide(size, screenshot_path, hook, slide_num)
    if tag:
        palette = {
            "before": ((180, 35, 35), (255, 255, 255)),
            "after": ((40, 80, 50), (255, 255, 255)),
            "neutral": ((17, 17, 17), (255, 255, 255)),
        }
        bg, fg = palette.get(tag_color or "neutral", palette["neutral"])
        _draw_corner_tag(img, tag, bg=bg, fg=fg)
    return img


def render_comparison_carousel(*, hook: str, before: Path,
                               after_screenshots: list[Path],
                               out_dir: Path,
                               sizes: tuple[tuple[int, int], ...] = (SIZE_9X16, SIZE_1X1)
                               ) -> dict:
    """3+ slide carousel: 1) hook + after hero, 2) BEFORE, 3..N) AFTER sections.

    Layout reads: 'rebuilt this' → see the bad one → see the good one.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    if not after_screenshots:
        raise ValueError("Need at least one after screenshot")

    slides: list[tuple[Path, str | None, str | None]] = []
    slides.append((after_screenshots[0], None, None))
    slides.append((before, "BEFORE", "before"))
    for s in after_screenshots:
        slides.append((s, "AFTER", "after"))

    total = len(slides)
    written: dict[str, list[str]] = {}
    for (W, H) in sizes:
        ratio_dir = out_dir / f"{W}x{H}"
        ratio_dir.mkdir(exist_ok=True)
        paths: list[str] = []
        for i, (shot, tag, color) in enumerate(slides, start=1):
            slide_hook = hook if i == 1 else None
            num = f"{i} / {total}"
            img = render_comparison_slide((W, H), shot, tag, color, num,
                                          slide_hook)
            p = ratio_dir / f"slide-{i:02d}.png"
            img.save(p, optimize=True)
            paths.append(str(p))
        written[f"{W}x{H}"] = paths
    return written
