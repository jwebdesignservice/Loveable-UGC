"""Pick the next niche + brand to build.

The orchestrator (Claude Code) is free to override this entirely — it can
invent its own niche + brand using its own reasoning and pass them to
`next-prompt --niche X --brand Y`. This module is just the deterministic
fallback for cases where the orchestrator doesn't want to think about it.
"""
from __future__ import annotations
import random
from dataclasses import dataclass

from .niches import CATALOG, NicheBrand, slug_for
from .prompts import build_prompt


@dataclass
class Design:
    niche: str
    brand: str
    tagline: str
    lovable_prompt: str
    slug: str


def pick_next_design(used_slugs: list[str]) -> Design:
    """Pick an unused entry from the catalog, or random if all are used."""
    used = set(used_slugs)
    candidates = [nb for nb in CATALOG if slug_for(nb) not in used]
    nb: NicheBrand = (random.choice(candidates) if candidates
                      else random.choice(CATALOG))
    return Design(
        niche=nb.niche, brand=nb.brand, tagline=nb.tagline,
        lovable_prompt=build_prompt(niche=nb.niche, brand=nb.brand),
        slug=slug_for(nb),
    )


def build_design(niche: str, brand: str, extra_notes: str | None = None
                 ) -> Design:
    """Wrap an explicit niche+brand into a Design with full prompt."""
    return Design(
        niche=niche, brand=brand, tagline="",
        lovable_prompt=build_prompt(niche=niche, brand=brand,
                                    extra_notes=extra_notes),
        slug=_slug(brand),
    )


def _slug(brand: str) -> str:
    return (brand.lower()
            .replace(" ", "-")
            .replace("/", "-")
            .replace("&", "and")
            .strip("-"))
