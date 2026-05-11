---
description: Run today's UGC content pipeline end-to-end — invent or reuse a Lovable site, render carousels, grade them, queue or post.
---

# /go — Daily UGC pipeline trigger

You are the **orchestrator**. The user typed `/go`. Run today's pipeline
end-to-end. Decisive, brief reports, no questions.

Everything in this pipeline runs through **your own Claude reasoning**
(authenticated via OAuth in Claude Code) plus the Lovable MCP connector.
The Python pipeline is a deterministic tool you call for templating,
rendering, state, and git. It does NOT call out to any LLM API.

## Step 1 — Read the plan

```bash
python -m pipeline plan
```

Parse the JSON. It tells you which `actions` to run in what order. Follow
that order.

## Step 2 — If a new site is needed, build it

If `actions[].kind == "build_site"` appears:

Launch the **site-builder** subagent. It will:
- Invent a fresh niche + brand (varying the vibe from what's already in `data/sites/`)
- Call `pipeline next-prompt` to get the templated Lovable prompt
- Call `mcp__lovable__create_project` with that prompt
- Iterate once if the build is weak
- Capture 4 section screenshots into `data/sites/<slug>/`
- Generate a dated BEFORE site for revamp carousels
- Write `data/sites/<slug>/content.json` with 4 carousel scripts
- Report back

When site-builder returns, verify:
- `data/sites/<slug>/01-hero.png` (and 02-04) exist
- `data/sites/<slug>/content.json` exists and has 4+ carousels

If site-builder reports the Lovable MCP isn't available, **stop the run**
and tell the user: *"Lovable connector isn't loaded in this Claude Code
session. Add it under Settings → Connectors → Lovable, then run /go
again."*

## Step 3 — Render the carousels

For each new site folder (one this turn, or any from prior runs that
have a `content.json` but no carousels yet):

```bash
python -m pipeline render-batch --site <slug>
```

This reads `data/sites/<slug>/content.json` and renders every carousel
listed at both 1080x1920 and 1080x1080. If a `<slug>-before` folder
exists, it also renders a comparison revamp carousel.

## Step 4 — Advisor review

Launch the **advisor** subagent. Tell it which carousel folders to
review (the ones just rendered).

Wait for it to finish. Read `data/last-advisor-review.json`.

For each verdict:
- `APPROVE` → leave it
- `REJECT` → delete the carousel folder (`rm -rf data/carousels/<name>`) and remove its entry from `data/state.json`
- `RETRY` → leave it but note it for the user

## Step 5 — Post to Instagram (if configured)

If `META_IG_ACCESS_TOKEN` and `META_IG_ACCOUNT_ID` are set in `.env`,
post the next-slot carousel using the Meta Graph API.

If they're not set (most builds before that's wired up), skip. Tell the
user which carousel is queued for the next slot and that posting will
happen once IG is configured.

## Step 6 — Commit and push

```bash
git add data/ .claude/ docs/ pipeline/
git commit -m "Daily UGC run: <design-slug> — N carousels approved"
git push origin claude/add-powershell-setup-script-tN8lz
```

If there's nothing to commit, skip.

## Step 7 — Report

A single short message back. Example:

```
Today's run
- Active design: Northbound (fitness coaching)
- Built: yes — preview https://northbound-abc.lovable.app
- Carousels rendered: 4 + 1 revamp (10 PNGs each)
- Advisor verdicts: 4 APPROVE, 1 RETRY (revamp comparison comp issue)
- Posted: skipped — IG token not configured
- Next slot: 19:00 UTC, queued northbound-01-site-previews
```

Tight. Numbers and outcomes. No commentary.

## Failure handling

Any step fails → stop, report the specific failure, leave state unchanged.
Don't silently retry.
