"""Day-level planner. Decides what to do when `/go` is invoked.

Outputs a JSON plan describing concrete actions for the orchestrator:
- whether a new Lovable site is needed
- which carousels are ready vs need rendering
- which slot is next for posting
"""
from __future__ import annotations
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone, time as dtime
from typing import Optional

from .config import CAROUSELS_PER_DESIGN
from .state import State, load, active_design, needs_new_design

POSTING_SLOTS_UTC = ["09:00", "13:00", "19:00"]


@dataclass
class Action:
    kind: str                 # e.g. "build_site", "render_carousels", "post"
    detail: dict = field(default_factory=dict)


@dataclass
class Plan:
    timestamp: str
    active_design_id: Optional[str]
    designs_count: int
    carousels_total: int
    carousels_unposted: int
    actions: list[Action] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def build_plan() -> Plan:
    state = load()
    now = datetime.now(timezone.utc)
    plan = Plan(
        timestamp=now.isoformat(timespec="seconds"),
        active_design_id=state.active_design_id,
        designs_count=len(state.designs),
        carousels_total=len(state.carousels),
        carousels_unposted=sum(1 for c in state.carousels if not c.posted),
    )

    if needs_new_design(state):
        plan.actions.append(Action(
            kind="build_site",
            detail={"reason": "no active design"
                    if not state.active_design_id else "current design spent"},
        ))
        plan.notes.append("Site-builder agent needed before content can be made.")
    else:
        d = active_design(state)
        if d is not None:
            remaining = CAROUSELS_PER_DESIGN - d.carousels_produced
            plan.notes.append(
                f"Active design '{d.id}' has {remaining} carousels remaining "
                f"of {CAROUSELS_PER_DESIGN}.")

    plan.actions.append(Action(
        kind="render_carousels",
        detail={"reads": "data/site-previews/<slug>/content.json",
                "command_per_site": "python -m pipeline render-batch --site <slug>"},
    ))

    plan.actions.append(Action(
        kind="advisor_review",
        detail={"target": "carousels rendered in this run",
                "reject_threshold": "any slide marked weak"},
    ))

    next_slot = _next_slot_after(now.strftime("%H:%M"))
    plan.actions.append(Action(
        kind="post_to_instagram",
        detail={"next_slot_utc": next_slot,
                "platforms": ["instagram"],
                "tiktok": "manual — slides only"},
    ))

    return plan


def _next_slot_after(hhmm: str) -> str:
    h, m = hhmm.split(":")
    cur = dtime(int(h), int(m))
    for slot in POSTING_SLOTS_UTC:
        sh, sm = slot.split(":")
        if dtime(int(sh), int(sm)) > cur:
            return slot
    return POSTING_SLOTS_UTC[0] + " (next day)"


def plan_to_dict(plan: Plan) -> dict:
    d = asdict(plan)
    d["actions"] = [{"kind": a.kind, "detail": a.detail} for a in plan.actions]
    return d


def plan_to_json(plan: Plan) -> str:
    return json.dumps(plan_to_dict(plan), indent=2)
