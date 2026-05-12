# Orchestration — how `/go` actually runs

Multi-agent system that turns a single trigger ("/go") into a finished
day of UGC content.

## The pieces

```
                ┌─────────────────────────────────┐
                │  TRIGGER                        │
                │  /go (manual)                   │
                │  or Windows Task Scheduler      │
                │  at 09:00 / 13:00 / 19:00       │
                └────────────────┬────────────────┘
                                 ↓
                ┌─────────────────────────────────┐
                │  ORCHESTRATOR                   │
                │  .claude/commands/go.md         │
                │  Reads `pipeline plan`,         │
                │  dispatches to subagents.       │
                └─┬───────────┬───────────┬───────┘
                  ↓           ↓           ↓
        ┌─────────────┐ ┌──────────┐ ┌────────────┐
        │ site-builder│ │ advisor  │ │ publisher  │
        │ Lovable MCP │ │ quality  │ │ (deferred  │
        │ + scrshots  │ │ review   │ │  to IG API)│
        └─────────────┘ └──────────┘ └────────────┘
                  ↓           ↓           ↓
        ┌─────────────────────────────────────────┐
        │  PYTHON PIPELINE                        │
        │  plan / auto / render / state           │
        └─────────────────────────────────────────┘
```

## Roles

| Role | Who | What it owns | What it doesn't |
| --- | --- | --- | --- |
| Orchestrator | `.claude/commands/go.md` | Reads plan, dispatches subagents, commits | Doesn't write content or build sites |
| site-builder | `.claude/agents/site-builder.md` | Talks to Lovable MCP, captures screenshots | Doesn't render slides or post |
| advisor | `.claude/agents/advisor.md` | Reviews every fresh carousel, grades, rejects bad ones | Doesn't build or post |
| publisher | (later) | IG Graph API upload at the right slot | Doesn't decide quality |
| Python pipeline | `pipeline/*.py` | Determinism: planning, rendering, state | No LLM calls inside steps the orchestrator runs |

## One trigger, one outcome

The user types `/go`. The orchestrator:

1. Runs `python -m pipeline plan` → gets a JSON action list
2. For each action in order:
   - `build_site` → launches site-builder subagent
   - `render_carousels` → runs `python -m pipeline auto --n 4`
   - `advisor_review` → launches advisor subagent
   - `post_to_instagram` → posts via Graph API if configured, else queues
3. Commits + pushes
4. Reports a short summary

## Scheduling (Windows Task Scheduler)

To run /go three times a day:

1. Open **Task Scheduler** → **Create Basic Task**
2. Name: `Loveable UGC daily`
3. Trigger: Daily at 09:00 → "New" two more times at 13:00 and 19:00
4. Action: **Start a program**
   - Program: `claude`
   - Arguments: `--print "/go"`
   - Start in: `C:\Users\Jack\Desktop\Loveable-UGC`
5. Save

(If `claude` isn't on PATH, point to its full install path,
e.g. `C:\Users\Jack\AppData\Local\Programs\claude-code\claude.exe`.)

## State at a glance

| File | What it tracks |
| --- | --- |
| `data/state.json` | Designs (Lovable builds) + carousels produced + posted flags |
| `data/last-advisor-review.json` | Most recent advisor verdicts (APPROVE / REJECT / RETRY) |
| `data/site-previews/<slug>/` | Real screenshots from Lovable for each design |
| `data/site-previews/<slug>-before/` | Generated dated BEFORE site for revamp carousels |
| `data/carousels/<slug>-NN-<pillar>/` | Rendered slide PNGs per carousel |

## Adding a new agent later

To add a new role (e.g. an A/B-test agent that picks the best-performing
hook for the next design):

1. Drop a markdown file in `.claude/agents/<role>.md` with `name`,
   `description`, `tools` frontmatter and a clear role spec
2. Add a step in `pipeline/plan.py` that surfaces the action
3. Add a dispatch branch in `.claude/commands/go.md`

That's the whole pattern.

## Failure semantics

- Each subagent reports a single short message back to the orchestrator
- Orchestrator stops the chain on any failure — does not silently
  proceed. Bad state is worse than no state.
- The user sees a one-line failure reason ("Lovable MCP not available",
  "Anthropic API key missing", "advisor REJECTED all carousels — see
  data/last-advisor-review.json")
