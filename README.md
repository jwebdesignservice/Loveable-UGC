# Loveable-UGC

Pipeline that builds image carousels for TikTok and Instagram showcasing
sites generated with Lovable.

## What it does (target state)

1. Pick a niche
2. Ask Lovable (via MCP) to build a landing page for that niche
3. Pull the site screenshot from Lovable, plus extra section captures
4. Generate N carousel variations (different hooks) using Claude
5. Render each as PNG slides — 1080x1920 (TikTok / Reels) and 1080x1080 (IG feed)
6. Each design is reused for ~12 carousels, then refreshed with a new niche

Instagram auto-posting will be wired later. For now the pipeline writes
slides to disk so you can review and post manually.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # add ANTHROPIC_API_KEY (+ LOVABLE_API_KEY once ready)
```

## Run the end-to-end demo

This generates fake placeholder screenshots, generates 3 carousel scripts,
and renders all slides. No API keys required — falls back to stub content
if `ANTHROPIC_API_KEY` isn't set.

```bash
python -m pipeline demo --n 3
```

Output lands in `data/carousels/<name>/{1080x1920,1080x1080}/slide-NN.png`.

## CLI

| Command | What it does |
| --- | --- |
| `python -m pipeline demo` | Placeholders → stub content → rendered carousels |
| `python -m pipeline placeholders --site <slug>` | Write fake site screenshots |
| `python -m pipeline render --site <slug> --hook "..." --carousel <name>` | Render one carousel |
| `python -m pipeline generate-content --niche ... --brand ... --prompt ...` | Generate N hook/caption sets via Claude |
| `python -m pipeline lovable list-tools` | List tools exposed by the Lovable MCP |
| `python -m pipeline lovable create-project --name ... --prompt ...` | Trigger a Lovable build |
| `python -m pipeline lovable get-project <id> --screenshot-out path.png` | Pull project + screenshot |

## Layout

| File | Purpose |
| --- | --- |
| `pipeline/config.py` | Paths, sizes, palette |
| `pipeline/state.py` | JSON state tracker (designs + carousels) |
| `pipeline/screenshots.py` | Placeholder site renderer (will be replaced by real captures) |
| `pipeline/renderer.py` | Slide composition (centered, site-first) |
| `pipeline/content.py` | Claude prompt → carousel scripts |
| `pipeline/lovable.py` | MCP client wrapper for mcp.lovable.dev |
| `pipeline/cli.py` | Entry point |

## Phase 2 (not done yet)

- Wire `lovable.create_project` into `demo` so real Lovable sites drive content
- Playwright-based scroll-and-clip to capture more sections than `get_project` alone
- Instagram Graph API posting on a schedule
- GitHub Actions cron at 09:00 / 13:00 / 19:00

## Examples

`examples/png-9x16/` and `examples/png-1x1/` hold the earlier text-first
mockups for reference. The new layout lives in `data/carousels/` after
running `python -m pipeline demo`.
