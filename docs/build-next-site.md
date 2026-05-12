# Recipe: build the next Lovable site for UGC

Runbook for **your** Claude Code session (the one with the Lovable MCP
connector). Triggered when the current design is spent or whenever you
want a fresh one.

You just say:

> Follow docs/build-next-site.md

No niche, no brand, no prompt. The pipeline picks everything.

---

## Step 1 — Pick the next design (autonomous)

```bash
python -m pipeline next-prompt --json
```

This calls Claude to invent:
- a niche that contrasts with what's already in `data/site-previews/`
- a fresh brand name
- a tagline
- the full detailed Lovable prompt (heavy on scroll animations, custom
  branding, $20K-agency feel)

The JSON output has: `slug`, `brand`, `niche`, `tagline`, `lovable_prompt`.

Save those fields. The `slug` is the folder name to use later.

If `ANTHROPIC_API_KEY` isn't set, it falls back to the static catalog
in `pipeline/niches.py`.

## Step 2 — Build the site in Lovable

Use the `mcp__lovable__create_project` tool with:
- `name` → the brand
- `initial_message` → the `lovable_prompt` from step 1

Wait for the build. Capture the returned `project_id`, `preview_url`,
and `screenshot`.

## Step 3 — Iterate if weak

Look at the screenshot. If the site is template-looking, missing
animations, or has filler copy, send one targeted message via
`mcp__lovable__send_message`:

- "Make the hero text reveal stagger on scroll. Add parallax on the hero
  imagery. Every section should fade and slide in as it enters the
  viewport. Smooth scroll throughout."
- "Replace placeholder copy with specific, in-brand lines for {brand}.
  No 'build faster, ship better' filler."
- "Add a horizontal scroll-scrub section for {feature}."

Stop after 1-2 rounds. If it still doesn't land, restart from step 1.

## Step 4 — Capture screenshots

Save 4-6 PNGs into `data/site-previews/<slug>/`:

```
data/site-previews/<slug>/01-hero.png
data/site-previews/<slug>/02-features.png
data/site-previews/<slug>/03-testimonials.png
data/site-previews/<slug>/04-footer.png
```

**Option A** — call `mcp__lovable__get_project` repeatedly while sending
scroll-by-section messages.

**Option B** — open `preview_url` in Playwright, scroll, screenshot each
section. Higher quality.

Number them in order so the carousel reads top-down.

## Step 5 — Optional: dated BEFORE site

For a one-shot-revamp carousel:

```bash
python -m pipeline ugly-site --site <slug>-before --brand "<Brand>"
```

Writes a deliberately 2005-era site to `data/site-previews/<slug>-before/`.

## Step 6 — Render the carousels

```bash
python -m pipeline auto --n 4
```

Renders 4 carousels per new site at both ratios. If a matching
`-before` folder exists, also renders a revamp comparison carousel.

Output lands in `data/carousels/<carousel-name>/{1080x1920,1080x1080}/`.

## Step 7 — Commit + push

```bash
git add data/site-previews data/carousels
git commit -m "Add <brand> site + carousels"
git push origin claude/add-powershell-setup-script-tN8lz
```

---

## Quick reference

| Command | Purpose |
| --- | --- |
| `python -m pipeline next-prompt --json` | Autonomous niche + brand + full Lovable prompt |
| `python -m pipeline next-prompt --niche property --brand LAWSITY` | Same, but override choices |
| `python -m pipeline ugly-site --site <slug>-before --brand "<Brand>"` | Generate a dated BEFORE site |
| `python -m pipeline auto --n 4` | Render carousels for any new sites |
| `python -m pipeline render --site <slug> --hook "..." --carousel <name>` | Render one specific carousel |
| `python -m pipeline render-comparison --before-site <slug>-before --after-site <slug> --hook "..." --carousel <name>` | One-shot revamp carousel |
