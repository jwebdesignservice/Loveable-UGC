"""Pick the next site design entirely autonomously.

`invent_next_design()` calls Claude to:
  - choose a niche that hasn't been done recently
  - invent a fresh brand name (no copying existing brands or generic words)
  - produce the full detailed Lovable prompt tuned for that brand

Returns a `Design` dict ready to feed into `mcp__lovable__create_project`.
"""
from __future__ import annotations
import json
import os
import random
from dataclasses import dataclass
from typing import Optional

from anthropic import Anthropic

from .niches import CATALOG, NicheBrand, slug_for
from .prompts import build_prompt, NICHES

MODEL = "claude-opus-4-7"


@dataclass
class InventedDesign:
    niche: str
    brand: str
    tagline: str
    lovable_prompt: str
    slug: str


SYSTEM = """You design fresh website concepts for short-form UGC content.
Each concept becomes a Lovable build that's screen-recorded for TikTok and
Instagram carousels.

Your job: invent ONE new design that's different from everything that
came before. Strong vibe, sharp brand name, on-trend niche.

Constraints:
- The brand name must feel real, distinctive, and pronounceable — not a
  generic dictionary word, not a trademark. 1-2 short words preferred.
- The niche should be something a real small/medium business would
  actually need a website for.
- Pick a vibe that contrasts with what's been built before — if previous
  sites were minimal warm tones, go bold and dark next; if previous were
  agency editorial, go technical SaaS next, etc.
- Don't repeat brand names or niches that already exist in the project.

Return JSON only:
{
  "niche": "short slug like 'skincare', 'property', 'saas', 'agency', etc.",
  "brand": "the invented brand name, real-feeling",
  "tagline": "one short line, lowercase, describes what they do",
  "vibe_notes": "two or three sentences of design direction unique to this brand: palette, typography pairing, imagery, signature animation moment. Vivid, specific, opinionated."
}
"""

USER_TEMPLATE = """Previously built designs (don't repeat the vibe):
{previous}

Allowed niches to pick from (or invent a related one):
{niche_options}

Invent the next design. Vary the vibe sharply from what's been built before."""


def invent_next_design(used_slugs: list[str]) -> InventedDesign:
    """Use Claude to invent a fresh niche + brand + detailed Lovable prompt."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return _fallback_design(used_slugs)

    previous = _previous_summary(used_slugs)
    niche_options = ", ".join(sorted(NICHES.keys()))

    client = Anthropic()
    msg = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM,
        messages=[{
            "role": "user",
            "content": USER_TEMPLATE.format(previous=previous,
                                            niche_options=niche_options),
        }],
    )
    text = "".join(b.text for b in msg.content if b.type == "text")
    text = _strip_fences(text)
    data = json.loads(text)

    niche = data["niche"]
    brand = data["brand"]
    tagline = data["tagline"]
    vibe_notes = data.get("vibe_notes")

    lovable_prompt = build_prompt(niche=niche, brand=brand,
                                  extra_notes=vibe_notes)
    return InventedDesign(
        niche=niche, brand=brand, tagline=tagline,
        lovable_prompt=lovable_prompt,
        slug=_slug(brand),
    )


def _fallback_design(used_slugs: list[str]) -> InventedDesign:
    """No API key — pick a random unused entry from the catalog."""
    used = set(used_slugs)
    candidates = [nb for nb in CATALOG if slug_for(nb) not in used]
    nb: NicheBrand = random.choice(candidates) if candidates else random.choice(CATALOG)
    return InventedDesign(
        niche=nb.niche, brand=nb.brand, tagline=nb.tagline,
        lovable_prompt=build_prompt(niche=nb.niche, brand=nb.brand),
        slug=slug_for(nb),
    )


def _previous_summary(used_slugs: list[str]) -> str:
    if not used_slugs:
        return "(nothing built yet — pick anything)"
    return "\n".join(f"- {slug}" for slug in used_slugs)


def _slug(brand: str) -> str:
    return (brand.lower()
            .replace(" ", "-")
            .replace("/", "-")
            .replace("&", "and")
            .strip("-"))


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[: text.rfind("```")]
    return text.strip()
