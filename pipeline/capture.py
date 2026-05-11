"""Real screenshot capture from Lovable preview URLs via Playwright.

Replaces the single-viewport `mcp__lovable__get_project` fallback with
proper multi-section captures suitable for carousel slides.

Outputs four PNGs into ``data/sites/<slug>/``:

    01-hero.png         viewport at the top of the page
    02-features.png     a section about one third down
    03-testimonials.png a section about two thirds down
    04-footer.png       the bottom of the page (footer)

Each image is a 1080-wide portrait crop at 2x device pixel ratio so the
renderer has enough resolution to compose 1080x1920 slides without
upscaling.
"""
from __future__ import annotations

import time
from pathlib import Path

VIEWPORT_W = 1080
VIEWPORT_H = 1920
SECTION_LABELS = ("01-hero", "02-features", "03-testimonials", "04-footer")
NAV_TIMEOUT_MS = 60_000
SETTLE_AFTER_LOAD_S = 2.0
SETTLE_AFTER_SCROLL_S = 0.8


def capture_site(preview_url: str, out_dir: Path) -> list[Path]:
    """Open ``preview_url`` and save four section screenshots into ``out_dir``.

    Returns the list of files written. Raises ``RuntimeError`` if Playwright
    isn't installed or Chromium can't launch.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        raise RuntimeError(
            "playwright is not installed. Run:\n"
            "  pip install playwright\n"
            "  playwright install chromium\n"
            "  sudo playwright install-deps  # Linux only"
        ) from e

    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": VIEWPORT_W, "height": VIEWPORT_H},
            device_scale_factor=2,
        )
        page = context.new_page()
        page.goto(preview_url, wait_until="networkidle",
                  timeout=NAV_TIMEOUT_MS)
        time.sleep(SETTLE_AFTER_LOAD_S)

        positions = _pick_scroll_positions(page)
        for label, y in zip(SECTION_LABELS, positions):
            page.evaluate(
                "(y) => window.scrollTo({top: y, behavior: 'instant'})", y
            )
            time.sleep(SETTLE_AFTER_SCROLL_S)
            target = out_dir / f"{label}.png"
            page.screenshot(path=str(target), full_page=False)
            written.append(target)

        browser.close()

    return written


def _pick_scroll_positions(page) -> list[int]:
    """Pick four Y-coordinates: hero, mid-1, mid-2, footer.

    Prefers semantic ``<section>`` boundaries when at least four exist;
    otherwise distributes evenly across the page height with the last
    position pinned to the bottom (footer).
    """
    total_height: int = page.evaluate("document.body.scrollHeight") or 0
    bottom = max(0, total_height - VIEWPORT_H)

    section_tops: list[int] = page.evaluate(
        """() => {
            const groups = [
              'section',
              'main > *',
              '[data-section]',
              '[role="region"]',
            ];
            for (const sel of groups) {
              const els = Array.from(document.querySelectorAll(sel));
              if (els.length >= 4) {
                return els
                  .map(e => Math.round(
                    e.getBoundingClientRect().top + window.scrollY))
                  .filter(t => t >= 0);
              }
            }
            return [];
        }"""
    )

    if section_tops and len(section_tops) >= 4:
        n = len(section_tops)
        return [
            section_tops[0],
            section_tops[n // 3],
            section_tops[(2 * n) // 3],
            bottom,
        ]

    return [0, total_height // 3, (2 * total_height) // 3, bottom]
