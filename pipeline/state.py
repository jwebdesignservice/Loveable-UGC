"""State tracker. One JSON file tracks designs (Lovable sites) and the
carousels produced from each. When a design hits CAROUSELS_PER_DESIGN
posts, it's marked spent and the niche-picker is asked for a new one.
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional

from .config import STATE_FILE, ensure_dirs, CAROUSELS_PER_DESIGN


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class Design:
    id: str
    niche: str
    prompt: str
    project_id: Optional[str] = None
    preview_url: Optional[str] = None
    deploy_url: Optional[str] = None
    screenshots: list[str] = field(default_factory=list)
    carousels_produced: int = 0
    created_at: str = field(default_factory=_now)
    spent: bool = False


@dataclass
class Carousel:
    id: str
    design_id: str
    pillar: str
    hook: str
    caption: str
    hashtags: list[str]
    slide_paths: list[str]
    created_at: str = field(default_factory=_now)
    posted: bool = False


@dataclass
class State:
    designs: list[Design] = field(default_factory=list)
    carousels: list[Carousel] = field(default_factory=list)
    active_design_id: Optional[str] = None


def load() -> State:
    ensure_dirs()
    if not STATE_FILE.exists():
        return State()
    raw = json.loads(STATE_FILE.read_text())
    designs = [Design(**d) for d in raw.get("designs", [])]
    carousels = [Carousel(**c) for c in raw.get("carousels", [])]
    return State(designs=designs, carousels=carousels,
                 active_design_id=raw.get("active_design_id"))


def save(state: State) -> None:
    ensure_dirs()
    STATE_FILE.write_text(json.dumps({
        "designs": [asdict(d) for d in state.designs],
        "carousels": [asdict(c) for c in state.carousels],
        "active_design_id": state.active_design_id,
    }, indent=2))


def active_design(state: State) -> Optional[Design]:
    if not state.active_design_id:
        return None
    return next((d for d in state.designs if d.id == state.active_design_id), None)


def needs_new_design(state: State) -> bool:
    d = active_design(state)
    return d is None or d.spent or d.carousels_produced >= CAROUSELS_PER_DESIGN


def add_design(state: State, design: Design) -> None:
    state.designs.append(design)
    state.active_design_id = design.id
    save(state)


def add_carousel(state: State, carousel: Carousel) -> None:
    state.carousels.append(carousel)
    design = next((d for d in state.designs if d.id == carousel.design_id), None)
    if design:
        design.carousels_produced += 1
        if design.carousels_produced >= CAROUSELS_PER_DESIGN:
            design.spent = True
    save(state)
