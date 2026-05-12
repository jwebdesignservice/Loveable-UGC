"""Real screenshot capture from Lovable preview URLs via Playwright.

Writes into ``data/site-previews/<slug>/``:

    00-fullpage.png       the entire scrollable page as one tall PNG
    01-hero.png           the hero section alone (first detected section)
    02-sections.png       next 2-3 sections below the hero, stitched
    03-sections.png       next 2-3 sections (if the site is long enough)
    ...                   variable count; the last group includes the footer

The implementation takes one Playwright full-page screenshot, then slices
it in PIL using detected ``<section>`` boundaries. One capture keeps
animation state consistent across crops and avoids re-scroll artifacts.
"""
from __future__ import annotations

import io
import math
import time
from pathlib import Path

from PIL import Image

VIEWPORT_W = 1080
VIEWPORT_H = 1920
NAV_TIMEOUT_MS = 60_000
VIEWPORT_SCREENSHOT_TIMEOUT_MS = 30_000
SETTLE_AFTER_LOAD_S = 2.0
SCROLL_DWELL_S = 0.8
PRE_SCROLL_DWELL_S = 0.6
TARGET_CHUNK_SIZE = 3

# Sites with scroll-scrub sections (pinned elements + GSAP ScrollTrigger,
# Lenis-driven parallax, etc.) report a `body.scrollHeight` that includes
# thousands of pixels of empty "runway" — scroll distance used to drive
# animations on a single pinned element. We cap each detected section so
# the resulting crops show actual content, not blank runway. One viewport
# is what the section is intended to look like for a first-time visitor.
MAX_SECTION_RUN_PX = VIEWPORT_H


def capture_site(preview_url: str, out_dir: Path) -> list[Path]:
    """Capture full-page + hero + grouped section PNGs from ``preview_url``.

    Returns the list of files written. Raises ``RuntimeError`` if Playwright
    isn't installed.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        raise RuntimeError(
            "playwright is not installed. Run:\n"
            "  pip install playwright\n"
            "  playwright install chromium\n"
            "  sudo .venv/bin/playwright install-deps  # Linux only"
        ) from e

    out_dir.mkdir(parents=True, exist_ok=True)
    fullpage_path = out_dir / "00-fullpage.png"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": VIEWPORT_W, "height": VIEWPORT_H},
            device_scale_factor=2,
        )
        page = context.new_page()
        page.goto(preview_url, wait_until="domcontentloaded",
                  timeout=NAV_TIMEOUT_MS)
        try:
            page.wait_for_load_state("networkidle", timeout=15_000)
        except Exception:
            pass  # Lovable previews sometimes keep a socket open forever
        time.sleep(SETTLE_AFTER_LOAD_S)

        # Soft-kill CSS animations/transitions so we don't get caught
        # mid-transition. JS-driven reveal animations (framer-motion, GSAP)
        # are still triggered naturally by the scroll loop below.
        page.add_style_tag(content="""
            *, *::before, *::after {
                animation-duration: 0s !important;
                animation-delay: 0s !important;
                transition-duration: 0s !important;
                transition-delay: 0s !important;
            }
        """)

        # Pre-scroll once to mount lazy content and fire IntersectionObserver
        # callbacks (whileInView, ScrollTrigger, etc.) for every section.
        page.evaluate(
            f"""async () => {{
                const step = window.innerHeight;
                const total = document.body.scrollHeight;
                for (let y = 0; y < total; y += step) {{
                    window.scrollTo({{top: y, behavior: 'instant'}});
                    await new Promise(r => setTimeout(
                        r, {int(PRE_SCROLL_DWELL_S * 1000)}));
                }}
            }}"""
        )
        time.sleep(0.5)

        section_bounds = _detect_section_bounds(page)
        scroll_height_css: int = page.evaluate(
            "document.body.scrollHeight") or 0
        content_bottom_css: int = _detect_content_bottom(page)
        # Stitch the whole scrollable area so scroll-scrub animations get
        # captured wherever they land, then trim to the last bit of real
        # content so the saved PNG isn't 95 % empty maroon.
        effective_height_css = max(
            content_bottom_css, VIEWPORT_H)

        full_img = _stitched_fullpage_capture(page, scroll_height_css)
        if effective_height_css * 2 < full_img.height:
            full_img = full_img.crop(
                (0, 0, full_img.width, effective_height_css * 2))
        full_img.save(fullpage_path, optimize=True)
        browser.close()

    crops = _slice_fullpage(
        fullpage_path=fullpage_path,
        out_dir=out_dir,
        section_bounds=section_bounds,
        total_height_css=effective_height_css,
    )
    return [fullpage_path, *crops]


def _detect_content_bottom(page) -> int:
    """Y coordinate (CSS px) of the bottom of the last real content element.

    Walks the DOM, ignores empty wrappers and zero-size elements, and
    returns the largest `top + height` it finds. Used to trim the
    scroll-runway off the saved full-page screenshot.
    """
    return page.evaluate(
        """() => {
            let lastBottom = 0;
            const els = document.querySelectorAll('*');
            for (const el of els) {
                const rect = el.getBoundingClientRect();
                if (rect.width < 16 || rect.height < 16) continue;
                const tag = el.tagName;
                const hasOwnText = (() => {
                    if (el.children.length > 0) return false;
                    const t = (el.textContent || '').trim();
                    return t.length > 1;
                })();
                const isMedia = (
                    tag === 'IMG' || tag === 'SVG' || tag === 'VIDEO' ||
                    tag === 'CANVAS' || tag === 'PICTURE'
                );
                const hasBgImage = (
                    getComputedStyle(el).backgroundImage !== 'none');
                if (!(hasOwnText || isMedia || hasBgImage)) continue;
                const bottom = rect.bottom + window.scrollY;
                if (bottom > lastBottom) lastBottom = bottom;
            }
            return Math.round(lastBottom);
        }"""
    ) or 0


def _stitched_fullpage_capture(page, total_height_css: int) -> Image.Image:
    """Scroll viewport-by-viewport, screenshot each, stitch in PIL.

    Bypasses Playwright's ``full_page=True`` because that path doesn't
    play nicely with JS-driven scroll reveal libraries (framer-motion,
    GSAP ScrollTrigger). Manually scrolling and dwelling at each
    position lets each section fade in before its capture.
    """
    if total_height_css <= 0:
        return Image.new(
            "RGB", (VIEWPORT_W * 2, VIEWPORT_H * 2), (255, 255, 255))

    positions: list[int] = []
    y = 0
    while y < total_height_css:
        positions.append(y)
        y += VIEWPORT_H
    bottom_y = max(0, total_height_css - VIEWPORT_H)
    if positions and positions[-1] < bottom_y:
        positions.append(bottom_y)

    img_w = VIEWPORT_W * 2
    img_h = max(VIEWPORT_H, total_height_css) * 2
    full = Image.new("RGB", (img_w, img_h), (255, 255, 255))

    for css_y in positions:
        page.evaluate(
            "(y) => window.scrollTo({top: y, behavior: 'instant'})", css_y
        )
        time.sleep(SCROLL_DWELL_S)
        png_bytes = page.screenshot(
            full_page=False,
            timeout=VIEWPORT_SCREENSHOT_TIMEOUT_MS,
        )
        chunk = Image.open(io.BytesIO(png_bytes))
        full.paste(chunk, (0, css_y * 2))

    return full


def _detect_section_bounds(page) -> list[dict]:
    """Return ``[{top, height}, ...]`` (CSS pixels) for top-level sections."""
    return page.evaluate(
        """() => {
            const selectors = ['section', 'main > *', '[data-section]'];
            for (const sel of selectors) {
                const els = Array.from(document.querySelectorAll(sel));
                const visible = els.filter(e => {
                    const r = e.getBoundingClientRect();
                    return r.height > 80;
                });
                if (visible.length >= 2) {
                    return visible.map(e => {
                        const r = e.getBoundingClientRect();
                        return {
                            top: Math.round(r.top + window.scrollY),
                            height: Math.round(r.height),
                        };
                    });
                }
            }
            return [];
        }"""
    )


def _slice_fullpage(*, fullpage_path: Path, out_dir: Path,
                    section_bounds: list[dict],
                    total_height_css: int) -> list[Path]:
    full = Image.open(fullpage_path)
    img_w, img_h = full.size
    scale = img_h / total_height_css if total_height_css else 2.0

    if section_bounds and len(section_bounds) >= 2:
        slots = _slots_from_sections(section_bounds, total_height_css)
    else:
        slots = _evenly_spaced_slots(total_height_css)

    written: list[Path] = []
    for label, top_css, bottom_css in slots:
        top = max(0, int(top_css * scale))
        bottom = min(img_h, int(bottom_css * scale))
        if bottom <= top:
            continue
        crop = full.crop((0, top, img_w, bottom))
        target = out_dir / label
        crop.save(target, optimize=True)
        written.append(target)
    return written


def _slots_from_sections(sections: list[dict], total_h: int
                         ) -> list[tuple[str, int, int]]:
    """Hero solo first; then 2-3-section groups. The last group extends to
    the page bottom so the footer rides along even if it lives outside the
    final ``<section>``."""
    sections = [
        {**s, "height": min(s["height"], MAX_SECTION_RUN_PX)}
        for s in sections
    ]
    hero = sections[0]
    rest = sections[1:]
    slots: list[tuple[str, int, int]] = [
        ("01-hero.png", hero["top"], hero["top"] + hero["height"])
    ]
    if not rest:
        return slots

    groups = _chunk_sections(rest)
    for i, group in enumerate(groups, start=2):
        first = group[0]
        last = group[-1]
        bottom = last["top"] + last["height"]
        if i - 2 == len(groups) - 1:
            bottom = max(bottom, total_h)
        slots.append((f"{i:02d}-sections.png", first["top"], bottom))
    return slots


def _chunk_sections(sections: list[dict]) -> list[list[dict]]:
    """Split into groups of 2-3, avoiding a dangling single."""
    n = len(sections)
    if n <= TARGET_CHUNK_SIZE:
        return [sections]
    n_groups = math.ceil(n / TARGET_CHUNK_SIZE)
    base, extra = divmod(n, n_groups)
    sizes = [base + 1 if i < extra else base for i in range(n_groups)]
    groups: list[list[dict]] = []
    idx = 0
    for size in sizes:
        groups.append(sections[idx:idx + size])
        idx += size
    return groups


def _evenly_spaced_slots(total_h: int) -> list[tuple[str, int, int]]:
    """Fallback when no sections were detected: 4 even slices."""
    if total_h <= 0:
        return []
    step = total_h // 4
    return [
        ("01-hero.png", 0, step),
        ("02-sections.png", step, step * 2),
        ("03-sections.png", step * 2, step * 3),
        ("04-sections.png", step * 3, total_h),
    ]
