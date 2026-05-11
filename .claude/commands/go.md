---
description: Run today's UGC content pipeline end-to-end — invent or reuse a Lovable site, generate carousels, grade them, queue or post.
---

# /go — Daily UGC pipeline trigger

You are the **orchestrator**. The user has typed `/go` and wants you to
run today's pipeline. Be decisive, dispatch to subagents, report back.

## Step 1 — Read the plan

```bash
python -m pipeline plan
```

Parse the JSON. It tells you which `actions` to run and in what order.
Always follow that order. Do NOT skip steps unless the plan says to.

## Step 2 — Dispatch each action

For each action in order:

### action.kind == "build_site"

Launch the **site-builder** subagent. Wait for it to return.

When it's done, verify by listing `data/sites/<slug>/`. Expect at least
two PNGs (hero + one other).

If site-builder reports the Lovable MCP isn't available in this session,
stop the pipeline and tell the user: *"The Lovable connector isn't
available in this Claude Code session. Add it in Settings → Connectors
→ Lovable, then run /go again."*

### action.kind == "render_carousels"

Run the command in `action.detail.command`:

```bash
python -m pipeline auto --n 4
```

Capture stdout. Confirm new folders appear under `data/carousels/`.

### action.kind == "advisor_review"

Launch the **advisor** subagent. Tell it which carousel folders to
review (the ones just rendered). Wait for it.

Read `data/last-advisor-review.json`. For each `REJECT` verdict, delete
the carousel folder. For `RETRY`, note it for the user — don't delete.

### action.kind == "post_to_instagram"

If `LOVABLE_API_KEY` and `META_IG_ACCESS_TOKEN` are set in the environment,
post the next-slot carousel to Instagram via the Graph API.

If those aren't set yet (most likely state during build-out), skip this
step and instead report which carousel is queued for the next slot.

## Step 3 — Commit and push

```bash
git add data/sites data/carousels data/state.json data/last-advisor-review.json
git commit -m "Daily UGC run: <design-slug> — N carousels approved"
git push origin claude/add-powershell-setup-script-tN8lz
```

If there's nothing new to commit, skip.

## Step 4 — Report

Write a short single message back to the user, e.g.:

```
Today's run:
- Active design: Northbound (fitness coaching)
- Built: yes (preview: <url>)
- Carousels rendered: 4 + 1 revamp
- Advisor: 4 APPROVE, 1 RETRY (slide composition issue on revamp)
- Posted: skipped — IG token not configured
- Next slot: 19:00 UTC, carousel northbound-01-site-previews
```

Keep it tight. The user wants outcomes, not commentary.

## Failure handling

Any step that fails: stop the chain, report the failure with the
specific error message, leave state unchanged. Do not silently retry —
the user needs to know what broke.
