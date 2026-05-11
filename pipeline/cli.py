"""CLI entry point.

  python -m pipeline demo                 # render placeholder carousel end-to-end
  python -m pipeline placeholders ...     # write fake site screenshots
  python -m pipeline render ...           # render one carousel from screenshots
  python -m pipeline generate-content ... # generate N carousel scripts via Claude
  python -m pipeline lovable list-tools   # introspect the Lovable MCP server
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
from typing import Optional

import click
from dotenv import load_dotenv

from . import content as content_mod
from . import lovable as lovable_mod
from . import screenshots as screenshots_mod
from . import state as state_mod
from .config import (CAROUSELS_DIR, SITES_DIR, SIZE_1X1, SIZE_9X16,
                     ensure_dirs)
from .renderer import render_carousel, render_comparison_carousel

load_dotenv()


@click.group()
def cli() -> None:
    """Loveable-UGC pipeline."""


@cli.command()
@click.option("--site", default="aurea-demo", help="Site slug.")
@click.option("--brand", default="Auréa", help="Brand name to render.")
def placeholders(site: str, brand: str) -> None:
    """Write fake-but-realistic site screenshots into data/sites/<site>/."""
    ensure_dirs()
    out = SITES_DIR / site
    paths = screenshots_mod.make_placeholder_site(out, brand=brand)
    click.echo(f"Wrote {len(paths)} screenshots to {out}")
    for p in paths:
        click.echo(f"  {p}")


@cli.command()
@click.option("--site", required=True, help="Site slug under data/sites/")
@click.option("--hook", required=True, help="Hook text for slide 1.")
@click.option("--carousel", "carousel_name", required=True,
              help="Output folder name under data/carousels/")
@click.option("--ratios", default="9x16,1x1",
              help="Comma-separated: 9x16,1x1")
def render(site: str, hook: str, carousel_name: str, ratios: str) -> None:
    """Render a carousel for one site + one hook."""
    site_dir = SITES_DIR / site
    if not site_dir.exists():
        raise click.ClickException(
            f"No site at {site_dir}. Run: python -m pipeline placeholders --site {site}")
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


@cli.command("generate-content")
@click.option("--niche", required=True)
@click.option("--brand", required=True)
@click.option("--description", required=True)
@click.option("--prompt", required=True,
              help="The Lovable prompt that built the site.")
@click.option("--url", default="", help="Live site URL.")
@click.option("--n", default=4, type=int)
@click.option("--out", "out_path", default="-",
              help="Output path or '-' for stdout.")
def generate_content(niche: str, brand: str, description: str, prompt: str,
                     url: str, n: int, out_path: str) -> None:
    """Generate N carousel scripts (hook, caption, hashtags) via Claude."""
    if content_mod.have_api_key():
        scripts = content_mod.generate_carousels(
            niche=niche, brand=brand, description=description,
            prompt=prompt, url=url, n=n,
        )
    else:
        click.echo("(no ANTHROPIC_API_KEY — using stub scripts)", err=True)
        scripts = content_mod.stub_carousels(n=n)

    payload = json.dumps([s.__dict__ for s in scripts], indent=2)
    if out_path == "-":
        click.echo(payload)
    else:
        Path(out_path).write_text(payload)
        click.echo(f"Wrote {out_path}")


@cli.command()
@click.option("--site", default="aurea-demo")
@click.option("--brand", default="Auréa")
@click.option("--n", default=3, type=int,
              help="How many distinct carousels to render.")
def demo(site: str, brand: str, n: int) -> None:
    """End-to-end demo: placeholders -> stub content -> rendered carousels."""
    ensure_dirs()

    site_dir = SITES_DIR / site
    if not list(site_dir.glob("*.png")):
        click.echo(f"Generating placeholder screenshots for {brand}...")
        screenshots_mod.make_placeholder_site(site_dir, brand=brand)

    scripts = (content_mod.generate_carousels(
        niche="skincare ecommerce", brand=brand,
        description=f"Clean botanical skincare brand. {brand}.",
        prompt=f"Build a warm botanical landing page for {brand}, a clean skincare brand.",
        url="https://example.lovable.app", n=n,
    ) if content_mod.have_api_key() else content_mod.stub_carousels(n=n))

    shots = sorted(site_dir.glob("*.png"))
    state = state_mod.load()

    for i, s in enumerate(scripts, start=1):
        cname = f"{site}-{i:02d}-{s.pillar}"
        click.echo(f"\n[{i}/{len(scripts)}] {s.hook}")
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
    state_mod.save(state)
    click.echo(f"\nDone. {len(scripts)} carousels in {CAROUSELS_DIR}.")


@cli.command("ugly-site")
@click.option("--site", required=True, help="Site slug under data/sites/")
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


@cli.command("comparison-demo")
@click.option("--brand", default="Auréa")
@click.option("--hook", default="rebuilt this in lovable. one prompt.")
def comparison_demo(brand: str, hook: str) -> None:
    """End-to-end demo of a BEFORE/AFTER comparison carousel."""
    ensure_dirs()

    after_dir = SITES_DIR / f"{brand.lower().replace(' ', '-')}-after"
    if not list(after_dir.glob("*.png")):
        click.echo(f"Generating polished AFTER site for {brand}...")
        screenshots_mod.make_placeholder_site(after_dir, brand=brand)

    before_dir = SITES_DIR / f"{brand.lower().replace(' ', '-')}-before"
    if not list(before_dir.glob("*.png")):
        click.echo(f"Generating dated BEFORE site for {brand}...")
        screenshots_mod.make_ugly_site(before_dir, brand=brand)

    before_shot = sorted(before_dir.glob("*.png"))[0]
    after_shots = sorted(after_dir.glob("*.png"))
    out_dir = CAROUSELS_DIR / f"{brand.lower().replace(' ', '-')}-revamp-demo"

    click.echo(f"\nRendering BEFORE/AFTER carousel: {hook}")
    written = render_comparison_carousel(
        hook=hook, before=before_shot,
        after_screenshots=after_shots, out_dir=out_dir,
    )
    click.echo(f"  -> {out_dir}")
    for ratio, paths in written.items():
        click.echo(f"     {ratio}: {len(paths)} slides")


@cli.command("render-comparison")
@click.option("--before-site", required=True,
              help="Slug under data/sites/ for the BEFORE site.")
@click.option("--after-site", required=True,
              help="Slug under data/sites/ for the AFTER site.")
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


@cli.group()
def lovable() -> None:
    """Lovable MCP commands (requires LOVABLE_API_KEY)."""


@lovable.command("list-tools")
def lovable_list_tools() -> None:
    """Print the tools exposed by the Lovable MCP server."""
    try:
        tools = lovable_mod.list_tools()
    except Exception as e:
        raise click.ClickException(str(e))
    for t in tools:
        click.echo(t)


@lovable.command("create-project")
@click.option("--name", required=True)
@click.option("--prompt", required=True,
              help="Initial message describing what to build.")
def lovable_create_project(name: str, prompt: str) -> None:
    """Create a Lovable project from a prompt and print the response."""
    try:
        result = lovable_mod.create_project(name=name, initial_message=prompt)
    except Exception as e:
        raise click.ClickException(str(e))
    click.echo(json.dumps(result, indent=2))


@lovable.command("get-project")
@click.argument("project_id")
@click.option("--screenshot-out", default=None,
              help="If set, save the screenshot PNG to this path.")
def lovable_get_project(project_id: str, screenshot_out: Optional[str]) -> None:
    try:
        result = lovable_mod.get_project(project_id)
    except Exception as e:
        raise click.ClickException(str(e))
    click.echo(json.dumps(result, indent=2))

    if screenshot_out and "screenshot" in result:
        path = lovable_mod.save_screenshot(result["screenshot"],
                                           Path(screenshot_out))
        click.echo(f"\nScreenshot saved to {path}")


if __name__ == "__main__":
    cli()
