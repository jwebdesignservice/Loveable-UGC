# Recipe: build the next Lovable site for UGC

This is a runbook for **your** Claude Code session (the one with the
Lovable MCP connector active). Run it whenever the current design has
been used for ~12 posts and you need a fresh one.

You ask Claude Code something like:

> follow docs/build-next-site.md

Or with overrides:

> follow docs/build-next-site.md — use the property niche, brand LAWSITY

Claude Code then does the steps below in order. Don't skip steps.

---

## Step 1 — Pick the niche and brand

Generate the prompt for the next design:

```bash
python -m pipeline next-prompt
```

This auto-picks the next niche from `pipeline/niches.py`, skipping any
brand that already has a folder under `data/sites/`. To force a choice:

```bash
python -m pipeline next-prompt --niche property --brand LAWSITY
```

Capture the output — that's the full Lovable prompt. Save the chosen
**slug** (lowercase brand with hyphens) for later steps. Example slug
for `LAWSITY` is `lawsity`.

## Step 2 — Build the site in Lovable

Use the `mcp__lovable__create_project` tool (the Lovable MCP connector).

- `name` → the brand (e.g. `LAWSITY`)
- `initial_message` → the full prompt from step 1
- Wait for the build to finish (the tool returns when ready)

Capture the returned `project_id`, `preview_url`, and any `screenshot` field.

## Step 3 — Iterate if needed

Look at the screenshot. If it's weak (template-looking, no animations,
generic copy), send one improvement message via `mcp__lovable__send_message`.
Common nudges that work:

- "Make the hero text reveal on scroll, staggered. Add parallax on the
  hero imagery. Sections fade and slide in as you scroll. Smooth scroll."
- "Replace the placeholder copy throughout with specific, in-brand copy
  for {brand}. No 'build faster, ship better'-style filler."
- "Add a horizontal scrub section for the {feature}."

Stop iterating after 1–2 rounds. We can re-roll the niche if it's bad.

## Step 4 — Capture screenshots

You want 4–6 sections of the finished site, saved as PNGs under
`data/sites/<slug>/`:

```
data/sites/lawsity/01-hero.png
data/sites/lawsity/02-listings.png
data/sites/lawsity/03-map.png
data/sites/lawsity/04-team.png
data/sites/lawsity/05-footer.png
```

Two ways to get them:

**Option A — use `get_project` repeatedly while sending scroll messages.**
The screenshot returned is the current viewport. Crude but works.

**Option B — Playwright on the preview URL.** Open the preview URL in a
headless browser, scroll, screenshot each section. Better quality.

Either way, save them numbered in order so the carousel reads top-down.

## Step 5 — (Optional) Generate a BEFORE site for revamp carousels

If you want a one-shot-revamp carousel off this design:

```bash
python -m pipeline ugly-site --site <slug>-before --brand "<Brand>"
```

This writes deliberately-dated PNGs to `data/sites/<slug>-before/`.
Skip if you only want clean-walkthrough carousels.

## Step 6 — Trigger the carousel pipeline

```bash
python -m pipeline auto --n 4
```

This scans `data/sites/`, finds any folder that doesn't have carousels
yet, and renders 4 fresh carousels per site at 1080x1920 and 1080x1080.
If a matching `-before` folder exists, it also renders a revamp
comparison carousel.

Outputs land in `data/carousels/<carousel-name>/{1080x1920,1080x1080}/`.

## Step 7 — Commit and push

```bash
git add data/sites data/carousels
git commit -m "Add <brand> site + carousels"
git push origin claude/add-powershell-setup-script-tN8lz
```

---

## Quick reference

| What | Command |
| --- | --- |
| Print next Lovable prompt | `python -m pipeline next-prompt` |
| Print a specific niche's prompt | `python -m pipeline next-prompt --niche skincare --brand "Auréa"` |
| Generate placeholder site (no Lovable) | `python -m pipeline placeholders --site <slug> --brand "<Brand>"` |
| Generate dated BEFORE site | `python -m pipeline ugly-site --site <slug>-before --brand "<Brand>"` |
| Render carousels for everything new | `python -m pipeline auto --n 4` |
| Render one specific carousel | `python -m pipeline render --site <slug> --hook "..." --carousel <name>` |
| One-shot revamp carousel | `python -m pipeline render-comparison --before-site <slug>-before --after-site <slug> --hook "..." --carousel <name>` |

## Niches in rotation

(see `pipeline/niches.py` to add more)

- property → LAWSITY
- skincare → Auréa
- saas → Pulseboard
- agency → Stoke & Stone
- restaurant → Sable
- fitness → Northbound
- fashion → Method/Form
- finance → Ledgerlight
