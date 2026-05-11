"""Detailed Lovable prompt builder.

Every prompt we send to Lovable should produce a site that:
  - looks like an award-winning agency build, not a template
  - has heavy, intentional scroll animations (this carousel reads as video)
  - is high-converting (proper sections, hierarchy, CTAs)
  - uses fully custom branding (palette, type, imagery direction)

`build_prompt(niche, brand)` returns the full string to feed to
`create_project` via the Lovable MCP.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class NicheSpec:
    niche: str
    palette: str
    typography: str
    imagery: str
    sections_extra: tuple[str, ...] = ()
    tone: str = "premium, modern, confident"


NICHES: dict[str, NicheSpec] = {
    "property": NicheSpec(
        niche="luxury property / real estate",
        palette=("deep charcoal, warm off-white, brass accent, one rich "
                 "tertiary (forest green or terracotta)"),
        typography="a refined display serif paired with a clean grotesque sans",
        imagery=("editorial architectural photography — wide-angle interiors, "
                 "golden-hour exteriors, and crops of materials (marble, "
                 "oak, brass). NO stock-photo realtors-in-suits."),
        sections_extra=(
            "featured listings grid with hover reveal of price + location",
            "interactive map section",
            "agent / team strip with portrait photography",
        ),
    ),
    "skincare": NicheSpec(
        niche="clean botanical skincare e-commerce",
        palette=("warm cream, sage green, deep olive, soft terracotta accent"),
        typography="a soft serif headline + a humanist sans for body",
        imagery=("hero product shots on natural stone or linen, single-stem "
                 "botanicals, soft natural light. Avoid bright white seamless."),
        sections_extra=(
            "ingredients deep-dive with iconography",
            "trust band (clinically tested, cruelty-free, vegan, etc.)",
            "product grid with cart-add hover state",
        ),
    ),
    "saas": NicheSpec(
        niche="AI / developer-facing SaaS tool",
        palette="near-black background, off-white text, one electric accent",
        typography="a tight modern sans (Inter / GT America vibe) at all weights",
        imagery=("dashboard mockups, product UI screens, code snippets in a "
                 "subtle terminal frame, gradient orbs as ambient backdrop"),
        sections_extra=(
            "interactive product demo / inline terminal",
            "logo wall of customers",
            "pricing tiers with a featured 'most popular' card",
            "live-typing code snippet hero",
        ),
        tone="confident, technical, fast",
    ),
    "agency": NicheSpec(
        niche="creative / branding agency portfolio",
        palette="off-black and bone white with one bold accent (acid green or magenta)",
        typography="oversized display serif (à la Migra or Editorial New) + mono accents",
        imagery=("case study screenshots, lifestyle behind-the-scenes shots, "
                 "behind-the-camera moments. Heavy use of typography as image."),
        sections_extra=(
            "work / case studies grid with hover video previews",
            "process / approach section",
            "services list with horizontal scroll",
        ),
        tone="bold, opinionated, design-led",
    ),
    "restaurant": NicheSpec(
        niche="modern restaurant / hospitality",
        palette="warm cream, deep burgundy or forest, brass accent",
        typography="an elegant serif (display + body) with a small caps subhead",
        imagery=("plated dishes from above, candle-lit interiors, "
                 "hands-pouring-wine moments. Moody, low-key, intimate."),
        sections_extra=(
            "menu preview with category tabs",
            "reservations CTA strip",
            "chef / story section with portrait",
        ),
    ),
    "fitness": NicheSpec(
        niche="performance fitness / coaching",
        palette="deep navy, off-white, one electric accent (volt yellow or red)",
        typography="a strong condensed grotesque (à la Druk / Inter Display)",
        imagery=("athletes mid-motion, gym detail shots (chalk, plates, "
                 "sweat). High-contrast, kinetic."),
        sections_extra=(
            "transformation results grid",
            "program tiers with month-to-month vs annual",
            "coach bio with stats",
        ),
        tone="kinetic, motivating, sharp",
    ),
    "fashion": NicheSpec(
        niche="independent fashion / streetwear",
        palette="off-black, bone, with one shock accent per collection",
        typography="an editorial serif + a wide-tracked all-caps sans for labels",
        imagery=("editorial lookbook photography, garment detail crops, "
                 "fabric textures, model portraits"),
        sections_extra=(
            "lookbook gallery with scroll-snap horizontal carousel",
            "drops / collections section",
            "shop-by-category grid",
        ),
        tone="editorial, confident, restrained",
    ),
    "finance": NicheSpec(
        niche="modern fintech / wealth app",
        palette="near-black, off-white, one trust-accent (deep teal or navy)",
        typography="a sharp sans throughout, tabular numerals visible",
        imagery=("app UI mockups, ambient gradient backgrounds, subtle "
                 "chart visualisations, no stock-photo handshakes"),
        sections_extra=(
            "live numbers / counter band",
            "compliance + security trust strip",
            "feature breakdown with phone mockups",
        ),
        tone="precise, trustworthy, modern",
    ),
}


def build_prompt(niche: str, brand: str, *,
                 extra_notes: str | None = None) -> str:
    spec = NICHES.get(niche)
    if not spec:
        spec = NicheSpec(
            niche=niche,
            palette="a tightly-restricted custom palette of 3-4 colours",
            typography="a custom display + body pairing chosen for the brand",
            imagery="custom, high-quality imagery appropriate for the niche",
        )

    extras = ""
    if spec.sections_extra:
        extras = "\n  - " + "\n  - ".join(spec.sections_extra)
    notes = f"\n\nAdditional notes: {extra_notes}" if extra_notes else ""

    return f"""Build me a super professional website for {spec.niche}. The brand is called {brand}.

Tone & design
- {spec.tone}. Think award-winning agency build, not a template.
- Fully custom branding: cohesive palette ({spec.palette}); typography is {spec.typography}; generous whitespace; consistent voice across every section.
- High-quality imagery: {spec.imagery}
- The whole site should feel like it costs $20K to commission, not $200.

Structure (high-converting)
- Hero: massive headline, supporting subhead, one primary CTA, secondary text link. Imagery anchors the right side or fills behind.
- Trust / social-proof band right under hero (logos, stat, or short testimonial line).
- Three to four feature or benefit sections, each visually distinct — one alternating-image layout, one full-bleed feature, one card grid.
- Testimonials section with at least three quotes and avatars.
- Pricing or service tiers if appropriate for the niche.
- FAQ with accordion behavior.
- Footer with newsletter signup, navigation, social, and a final CTA repeat.{extras and chr(10) + "- Also include:" + extras}

Critical — animations (this site will be screen-recorded for short-form video)
- Heavy emphasis on advanced, intentional scroll animations.
- Hero text reveals on load with a staggered, slightly-delayed motion.
- Parallax on the hero imagery.
- Every major section fades + slides in as it enters the viewport, with a slight stagger between children.
- Include at least one sticky scroll-scrub section that pins while the user scrolls and reveals content as they go (e.g. a feature with a 3-step explainer).
- Smooth scroll behavior throughout.
- Subtle hover micro-interactions on every interactive element: links, buttons, cards, images.
- A horizontal-scroll section somewhere (logo wall, testimonials, lookbook, or work grid) that doubles as a scrub moment.
- Every animation should feel cinematic and intentional — these screen recordings need to look impressive.

Build hygiene
- Use modern, accessible markup. Mobile-first. No layout shift on load.
- Keep copy real, specific, and in-brand — no lorem ipsum, no "Build faster. Ship better." filler.
- Use real-feeling placeholder content (named team members, real-sounding testimonials, plausible product names).{notes}
"""
