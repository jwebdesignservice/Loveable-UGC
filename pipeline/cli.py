"""CLI entry point — deterministic. All LLM-driven thinking happens in
the Claude Code orchestrator. The pipeline is a tool the orchestrator
calls; it does not call out to LLMs itself.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional

import click
from dotenv import load_dotenv

from . import content as content_mod
from . import design as design_mod
from . import niches as niches_mod
from . import plan as plan_mod
from . import prompts as prompts_mod
from . import screenshots as screenshots_mod
from . import state as state_mod
from .config import (CAROUSELS_DIR, SITES_DIR, SIZE_1X1, SIZE_9X16,
                     ensure_dirs)
from .renderer import render_carousel, render_comparison_carousel

load_dotenv()


@click.group()
def cli() -> None:
    """Loveable-UGC pipeline."""


# ---------------------------------------------------------------- planning


@cli.command()
def plan() -> None:
    """Print today's action plan as JSON for the orchestrator to consume."""
    p = plan_mod.build_plan()
    click.echo(plan_mod.plan_to_json(p))


@cli.command("next-prompt")
@click.option("--niche", default=None,
              help="Niche key (see pipeline/niches.py CATALOG). Auto-picks from rotation if omitted.")
@click.option("--brand", default=None,
              help="Brand name. Auto-picks from rotation if omitted.")
@click.option("--extra-notes", default=None,
              help="Free-text additions appended to the prompt (vibe direction, specific copy hints, etc).")
@click.option("--json", "as_json", is_flag=True,
              help="Print JSON with slug/brand/niche/prompt instead of just the prompt.")
def next_prompt(niche: str | None, brand: str | None,
                extra_notes: str | None, as_json: bool) -> None:
    """Build a detailed Lovable prompt.

    With --niche AND --brand: builds the prompt for exactly that.
    With neither: picks the next entry from the static catalog.
    The orchestrator typically passes both because it has its own
    reasoning about what to build next.
    """
    if niche and brand:
        d = design_mod.build_design(niche=niche, brand=brand,
                                    extra_notes=extra_notes)
    else:
        used = _used_slugs()
        d = design_mod.pick_next_design(used_slugs=used)
        if niche or brand:
            d = design_mod.build_design(
                niche=niche or d.niche,
                brand=brand or d.brand,
                extra_notes=extra_notes,
            )

    if as_json:
        click.echo(json.dumps({
            "slug": d.slug, "brand": d.brand, "niche": d.niche,
            "tagline": d.tagline, "lovable_prompt": d.lovable_prompt,
        }, indent=2))
    else:
        click.echo(f"# {d.brand} ({d.niche}) — slug: {d.slug}", err=True)
        click.echo(d.lovable_prompt)


# ------------------------------------------------------------ placeholders


@cli.command()
@click.option("--site", default="aurea-demo", help="Site slug.")
@click.option("--brand", default="Auréa", help="Brand name to render.")
def placeholders(site: str, brand: str) -> None:
    """Write fake-but-realistic site screenshots into data/site-previews/<site>/."""
    ensure_dirs()
    out = SITES_DIR / site
    paths = screenshots_mod.make_placeholder_site(out, brand=brand)
    click.echo(f"Wrote {len(paths)} screenshots to {out}")
    for p in paths:
        click.echo(f"  {p}")


@cli.command()
@click.option("--url", required=True,
              help="Lovable preview URL (e.g. https://sable-restaurant.lovable.app).")
@click.option("--site", required=True,
              help="Slug; screenshots saved to data/site-previews/<slug>/.")
def capture(url: str, site: str) -> None:
    """Capture four section screenshots from a Lovable preview URL.

    Uses Playwright + headless Chromium. Install once with:
      pip install playwright && playwright install chromium
    """
    from .capture import capture_site
    ensure_dirs()
    out = SITES_DIR / site
    paths = capture_site(url, out)
    click.echo(f"Wrote {len(paths)} screenshots to {out}")
    for p in paths:
        click.echo(f"  {p}")


@cli.command()
@click.option("--input", "input_dir", required=True,
              help="Folder containing images to stitch (sorted by filename).")
@click.option("--output", "output_path", required=True,
              help="Output PNG path.")
@click.option("--width", default=None, type=int,
              help="Target width in px. Defaults to the narrowest input.")
def stitch(input_dir: str, output_path: str, width: int | None) -> None:
    """Stitch images vertically into one tall PNG.

    The manual fallback for sites where the automated `capture` command
    fights scroll-scrub animations. Save your browser screenshots into a
    folder with sortable names (01-hero.png, 02-food.png, ...) and run
    this command.
    """
    from PIL import Image

    in_dir = Path(input_dir)
    images_in = sorted(
        list(in_dir.glob("*.png")) + list(in_dir.glob("*.jpg"))
        + list(in_dir.glob("*.jpeg")) + list(in_dir.glob("*.webp"))
    )
    if not images_in:
        raise click.ClickException(f"No images found in {in_dir}")

    imgs = [Image.open(p).convert("RGB") for p in images_in]
    target_w = width or min(img.width for img in imgs)

    resized: list = []
    for img in imgs:
        if img.width != target_w:
            new_h = int(img.height * (target_w / img.width))
            img = img.resize((target_w, new_h), Image.LANCZOS)
        resized.append(img)

    total_h = sum(img.height for img in resized)
    stitched = Image.new("RGB", (target_w, total_h), (255, 255, 255))
    y = 0
    for img in resized:
        stitched.paste(img, (0, y))
        y += img.height

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    stitched.save(out, optimize=True)
    click.echo(f"Wrote {out} ({target_w}x{total_h})")
    for p in images_in:
        click.echo(f"  + {p}")


@cli.command("ugly-site")
@click.option("--site", required=True, help="Site slug under data/site-previews/")
@click.option("--brand", required=True, help="Brand name to render.")
@click.option("--tagline", default="Your one-stop online destination.")
def ugly_site(site: str, brand: str, tagline: str) -> None:
    """Write a deliberately bad-looking BEFORE site (90s/2000s vibe)."""
    ensure_dirs()
    out = SITES_DIR / site
    paths = screenshots_mod.make_ugly_site(out, brand=brand, tagline=tagline)
    click.echo(f"Wrote {len(paths)} ugly screenshots to {out}")
    for p in paths:
        click.echo(f"  {p}")


# ----------------------------------------------------------------- render


@cli.command()
@click.option("--site", required=True, help="Site slug under data/site-previews/")
@click.option("--hook", required=True, help="Hook text for slide 1.")
@click.option("--carousel", "carousel_name", required=True,
              help="Output folder name under data/carousels/")
@click.option("--ratios", default="9x16,1x1",
              help="Comma-separated: 9x16,1x1")
def render(site: str, hook: str, carousel_name: str, ratios: str) -> None:
    """Render a single carousel for one site + one hook."""
    site_dir = SITES_DIR / site
    if not site_dir.exists():
        raise click.ClickException(f"No site at {site_dir}.")
    shots = sorted(site_dir.glob("*.png"))
    if not shots:
        raise click.ClickException(f"No screenshots found in {site_dir}")

    sizes = []
    if "9x16" in ratios:
        sizes.append(SIZE_9X16)
    if "1x1" in ratios:
        sizes.append(SIZE_1X1)

    out_dir = CAROUSELS_DIR / carousel_name
    written = render_carousel(hook=hook, screenshots=shots,
                              out_dir=out_dir, sizes=tuple(sizes))
    for ratio, paths in written.items():
        click.echo(f"{ratio}:")
        for p in paths:
            click.echo(f"  {p}")


@cli.command("render-batch")
@click.option("--site", required=True,
              help="Site slug under data/site-previews/")
@click.option("--content", "content_path", default=None,
              help="Path to JSON with carousels. Defaults to data/site-previews/<slug>/content.json")
def render_batch(site: str, content_path: str | None) -> None:
    """Render every carousel listed in a content JSON file for one site.

    The orchestrator writes the JSON (with hooks/captions/hashtags it
    invented) and then calls this command. See content.CONTENT_JSON_SCHEMA
    for the expected shape.
    """
    site_dir = SITES_DIR / site
    if not site_dir.exists():
        raise click.ClickException(f"No site at {site_dir}.")
    shots = sorted(site_dir.glob("*.png"))
    if not shots:
        raise click.ClickException(f"No screenshots found in {site_dir}")

    path = Path(content_path) if content_path else site_dir / "content.json"
    if not path.exists():
        raise click.ClickException(
            f"No content.json at {path}.\n"
            f"The orchestrator should write it. Schema:\n\n"
            f"{content_mod.CONTENT_JSON_SCHEMA}"
        )

    scripts = content_mod.load_from_json(path)
    state = state_mod.load()

    for i, s in enumerate(scripts, start=1):
        cname = f"{site}-{i:02d}-{s.pillar}"
        click.echo(f"[{i}/{len(scripts)}] {s.hook}")
        written = render_carousel(hook=s.hook, screenshots=shots,
                                  out_dir=CAROUSELS_DIR / cname)
        click.echo(f"  -> {CAROUSELS_DIR / cname}")
        for ratio in written:
            click.echo(f"     {ratio}: {len(written[ratio])} slides")

        state.carousels.append(state_mod.Carousel(
            id=cname, design_id=site, pillar=s.pillar,
            hook=s.hook, caption=s.caption, hashtags=s.hashtags,
            slide_paths=[p for paths in written.values() for p in paths],
        ))

    before_slug = f"{site}-before"
    before_dir = SITES_DIR / before_slug
    if before_dir.exists() and list(before_dir.glob("*.png")):
        before_shot = sorted(before_dir.glob("*.png"))[0]
        revamp_hook = "rebuilt this in lovable. one prompt."
        cname = f"{site}-revamp"
        click.echo(f"[revamp] {revamp_hook}")
        written = render_comparison_carousel(
            hook=revamp_hook, before=before_shot,
            after_screenshots=shots,
            out_dir=CAROUSELS_DIR / cname,
        )
        click.echo(f"  -> {CAROUSELS_DIR / cname}")
        state.carousels.append(state_mod.Carousel(
            id=cname, design_id=site, pillar="one-shot-revamp",
            hook=revamp_hook,
            caption=f"one prompt in lovable turned the old site into this.",
            hashtags=["#lovable", "#webdesign", "#revamp"],
            slide_paths=[p for paths in written.values() for p in paths],
        ))

    state_mod.save(state)
    click.echo(f"\nDone. {len(state.carousels)} carousels total.")


@cli.command("render-comparison")
@click.option("--before-site", required=True,
              help="Slug under data/site-previews/ for the BEFORE site.")
@click.option("--after-site", required=True,
              help="Slug under data/site-previews/ for the AFTER site.")
@click.option("--hook", required=True)
@click.option("--carousel", "carousel_name", required=True)
def render_comparison_cmd(before_site: str, after_site: str, hook: str,
                          carousel_name: str) -> None:
    """Render a BEFORE/AFTER carousel from two existing site folders."""
    before_dir = SITES_DIR / before_site
    after_dir = SITES_DIR / after_site
    if not before_dir.exists():
        raise click.ClickException(f"No site at {before_dir}")
    if not after_dir.exists():
        raise click.ClickException(f"No site at {after_dir}")
    before_shots = sorted(before_dir.glob("*.png"))
    after_shots = sorted(after_dir.glob("*.png"))
    if not before_shots or not after_shots:
        raise click.ClickException("Both sites need at least one screenshot")
    out = CAROUSELS_DIR / carousel_name
    written = render_comparison_carousel(
        hook=hook, before=before_shots[0],
        after_screenshots=after_shots, out_dir=out,
    )
    for ratio, paths in written.items():
        click.echo(f"{ratio}:")
        for p in paths:
            click.echo(f"  {p}")


# --------------------------------------------------------- offline smoke


@cli.command()
@click.option("--site", default="aurea-demo")
@click.option("--brand", default="Auréa")
@click.option("--n", default=3, type=int)
def demo(site: str, brand: str, n: int) -> None:
    """Offline smoke test: placeholders + stub content -> rendered carousels.

    Only use this to verify the renderer works locally. In a real run the
    orchestrator drives the whole flow and content.json is written by
    Claude Code, not by stubs.
    """
    ensure_dirs()

    site_dir = SITES_DIR / site
    if not list(site_dir.glob("*.png")):
        click.echo(f"Generating placeholder screenshots for {brand}...")
        screenshots_mod.make_placeholder_site(site_dir, brand=brand)

    scripts = content_mod.stub_carousels(n=n)
    state = state_mod.load()
    shots = sorted(site_dir.glob("*.png"))

    for i, s in enumerate(scripts, start=1):
        cname = f"{site}-{i:02d}-{s.pillar}"
        click.echo(f"[{i}/{n}] {s.hook}")
        written = render_carousel(hook=s.hook, screenshots=shots,
                                  out_dir=CAROUSELS_DIR / cname)
        state.carousels.append(state_mod.Carousel(
            id=cname, design_id=site, pillar=s.pillar,
            hook=s.hook, caption=s.caption, hashtags=s.hashtags,
            slide_paths=[p for paths in written.values() for p in paths],
        ))
    state_mod.save(state)
    click.echo(f"\nDone.")


if __name__ == "__main__":
    cli()


def _used_slugs() -> list[str]:
    if not SITES_DIR.exists():
        return []
    return [p.name for p in SITES_DIR.iterdir()
            if p.is_dir() and p.name not in {".gitkeep"}
            and not p.name.endswith("-before")]
