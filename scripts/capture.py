"""Headless screenshot capture for a deployed site.

Used by .github/workflows/capture-site.yml — opens a URL in chromium,
takes a full-page screenshot, resizes to 1080 wide, splits into N
portrait sections, and writes them as 01-hero.png .. 0N-section.png
into data/sites/<slug>/.
"""
from __future__ import annotations
import asyncio
import sys
from pathlib import Path

from PIL import Image
from playwright.async_api import async_playwright


SECTION_NAMES = [
    "01-hero.png",
    "02-features.png",
    "03-testimonials.png",
    "04-footer.png",
]


async def capture(url: str, out_dir: Path, n_sections: int = 4,
                  target_width: int = 1080) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            device_scale_factor=1.5,
        )
        page = await context.new_page()
        print(f"Loading {url} ...")
        await page.goto(url, wait_until="networkidle", timeout=90000)
        await page.wait_for_timeout(4000)
        png_bytes = await page.screenshot(full_page=True, type="png")
        await browser.close()

    full_path = out_dir / "_full.png"
    full_path.write_bytes(png_bytes)
    img = Image.open(full_path).convert("RGB")
    print(f"Captured: {img.width}x{img.height}")

    if img.width != target_width:
        scale = target_width / img.width
        img = img.resize((target_width, int(img.height * scale)),
                         Image.LANCZOS)
        print(f"Resized to: {img.width}x{img.height}")

    h = img.height
    section_h = h // n_sections
    written: list[Path] = []
    for i in range(n_sections):
        y1 = i * section_h
        y2 = (i + 1) * section_h if i < n_sections - 1 else h
        crop = img.crop((0, y1, target_width, y2))
        name = SECTION_NAMES[i] if i < len(SECTION_NAMES) else f"{i+1:02d}-section.png"
        out_path = out_dir / name
        crop.save(out_path, optimize=True)
        print(f"  wrote {out_path}  ({crop.width}x{crop.height})")
        written.append(out_path)

    full_path.unlink()
    return written


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: capture.py <url> <slug>", file=sys.stderr)
        sys.exit(1)
    url = sys.argv[1]
    slug = sys.argv[2]
    out = Path("data/sites") / slug
    asyncio.run(capture(url, out))
