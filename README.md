# Loveable-UGC

Autonomous pipeline that produces 3 image carousels per day for TikTok
and Instagram showcasing sites built with Lovable.

You type `/go`. The system invents a niche, builds a real site in Lovable,
captures screenshots, writes hooks/captions, renders carousels at both
ratios, grades them, and queues the day's post.

## How it runs (OAuth-only — no API keys needed)

All thinking happens inside Claude Code (authenticated via your Pro plan
OAuth). The Python pipeline is purely deterministic — templating, PIL
rendering, state tracking, git. It does not call any LLM API.

```
USER
  │
  │  /go    (manual or Windows Task Scheduler)
  ↓
ORCHESTRATOR ────► PYTHON PIPELINE (deterministic)
  │  Claude            plan / render / state / git
  │  reasoning
  ↓
SUBAGENTS
  ├─ site-builder  ──► Lovable MCP (mcp__lovable__*)
  └─ advisor       ──► reads PNGs, grades, writes JSON verdicts
```

## Prerequisites

1. Claude Code installed (desktop or web)
2. Lovable Pro plan
3. The Lovable MCP connector added in Claude Code:
   - Settings → Connectors → Add custom connector
   - URL: `https://mcp.lovable.dev`
   - Authenticate via OAuth (one-time)
4. Python 3.11+ with `pip install -r requirements.txt`

That's it. No API keys.

## Quick start

In your Claude Code session, point at this repo and run:

```
/go
```

The orchestrator (`.claude/commands/go.md`) takes it from there.

## Manual one-off commands

| Command | What |
| --- | --- |
| `python -m pipeline plan` | Print today's action plan as JSON |
| `python -m pipeline next-prompt --niche X --brand "Y"` | Build a detailed Lovable prompt |
| `python -m pipeline placeholders --site X --brand "Y"` | Generate fake site screenshots (test only) |
| `python -m pipeline ugly-site --site X-before --brand "Y"` | Generate a dated BEFORE site for revamp carousels |
| `python -m pipeline render-batch --site X` | Render every carousel listed in `data/site-previews/X/content.json` |
| `python -m pipeline render-comparison --before-site X-before --after-site X --hook "..." --carousel name` | Render one BEFORE/AFTER carousel |
| `python -m pipeline demo` | Offline smoke test (stub content + placeholders) |

## Layout

```
.claude/
  agents/
    site-builder.md        # invents niche, builds Lovable site, writes content.json
    advisor.md             # grades carousels before they're posted
  commands/
    go.md                  # /go slash command — orchestrator
pipeline/
  config.py                # paths, sizes, palette
  state.py                 # JSON state (designs + carousels)
  plan.py                  # decides today's actions
  prompts.py               # detailed Lovable prompt template
  niches.py                # static catalog fallback
  design.py                # picks niche + brand (catalog-based)
  screenshots.py           # placeholder + ugly-site generators
  renderer.py              # slide composition (PIL)
  content.py               # carousel script I/O
  cli.py                   # entry point
data/
  sites/<slug>/            # screenshots from Lovable for each design
  sites/<slug>/content.json # carousel hooks/captions written by orchestrator
  sites/<slug>-before/     # dated BEFORE site for revamp content
  carousels/<name>/        # rendered slides (1080x1920 + 1080x1080)
  state.json               # design + carousel tracking
docs/
  build-next-site.md       # site-builder recipe (verbose)
  orchestration.md         # multi-agent architecture + scheduling
```

## State files

| File | What it tracks |
| --- | --- |
| `data/state.json` | All designs (Lovable builds) and carousels rendered |
| `data/last-advisor-review.json` | Most recent advisor verdicts |
| `data/site-previews/<slug>/content.json` | Carousel scripts for one design |

## Scheduling (Windows)

Open Task Scheduler → Create Basic Task. Triggers at 09:00 / 13:00 / 19:00:

```
Program:    claude
Arguments:  --print "/go"
Start in:   C:\Users\Jack\Desktop\Loveable-UGC
```

See `docs/orchestration.md` for the long version.

## What's NOT done yet

- Instagram Graph API auto-post (currently /go skips this step)
- Playwright multi-section screenshot capture (site-builder falls back to single `get_project` viewport for now)
- Performance feedback loop (advisor doesn't yet learn from posted-vs-skipped data)
