"""Niche + brand-name catalog for rotation.

Pipeline cycles through these so successive designs don't look the same.
When all are used (tracked by `Design` records in state), it loops back.
Order is intentional — varied vibes side-by-side.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class NicheBrand:
    niche: str            # key into prompts.NICHES
    brand: str            # generated brand name
    tagline: str          # used by content generator for hooks


CATALOG: list[NicheBrand] = [
    NicheBrand("property", "LAWSITY",
               "Premium property experiences."),
    NicheBrand("skincare", "Auréa",
               "Clean botanical skincare."),
    NicheBrand("saas", "Pulseboard",
               "AI scheduling for teams that move fast."),
    NicheBrand("agency", "Stoke & Stone",
               "Independent branding studio."),
    NicheBrand("restaurant", "Sable",
               "Modern seasonal dining."),
    NicheBrand("fitness", "Northbound",
               "Performance coaching for hybrid athletes."),
    NicheBrand("fashion", "Method/Form",
               "Considered, drop-based ready-to-wear."),
    NicheBrand("finance", "Ledgerlight",
               "Wealth management for builders."),
]


def next_niche(used_slugs: list[str]) -> NicheBrand:
    """Pick the first catalog entry whose brand hasn't been used yet."""
    used = set(used_slugs)
    for nb in CATALOG:
        slug = nb.brand.lower().replace(" ", "-").replace("/", "-")
        if slug not in used:
            return nb
    return CATALOG[len(used) % len(CATALOG)]


def slug_for(nb: NicheBrand) -> str:
    return nb.brand.lower().replace(" ", "-").replace("/", "-")
