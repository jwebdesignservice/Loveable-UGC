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
- {spec.tone}. Think award-winning agency build (think Sites of the Day, Awwwards / Godly), not a Webflow template, not a SaaS landing page generator output.
- Fully custom branding: cohesive palette ({spec.palette}); typography is {spec.typography}; consistent voice across every section.
- High-quality imagery: {spec.imagery}
- The whole site should feel like a real $20K agency commission. No defaults, no obvious template moves.

Layout & spacing — critical, do not skip
- Use a real baseline grid: 8px increments for all spacing. Section padding should be at least 96px top and bottom on desktop, 64px on mobile. Never let a section feel cramped.
- Elements MUST NOT overlap unless intentionally layered (e.g. an image bleeding behind text). No accidental overlapping cards, buttons, navs, or text blocks. No content clipping at any breakpoint.
- Use a consistent max-width content container (1200-1280px) and centre it. No edge-to-edge text on desktop.
- Hierarchy is enforced by spacing, weight, and scale — not by random colour changes. Each section has a clear primary, secondary, tertiary element.
- Line-height: 1.5 for body copy, 1.1-1.2 for display headlines. Don't use the same line-height everywhere.
- Buttons and form fields share a single height system (e.g. 48px / 56px). Don't mix heights randomly.
- Cards in a grid must all be the same height. If content differs, pad to match — never let cards "jog" at different heights.

Typography — be specific, not generic
- Pair TWO fonts deliberately: {spec.typography}. Don't fall back to "Inter for everything" or "default system font". Pick real, distinctive faces.
- Use the display face for h1 and h2 only. Use the body face for h3, h4, body, captions, buttons.
- Type scale: display ~64-96px, h2 ~40-56px, h3 ~28-32px, body ~17-18px, caption ~13-14px. Tighter on mobile.
- Numerals should be tabular when used in stats/pricing.
- Avoid system font fallbacks visually — every text block should look intentional.

Structure (high-converting)
- Hero: a single, specific, in-brand headline (NOT "Build faster, ship better" or "The future of X"). Real subhead. One primary CTA, one secondary text link. Hero imagery anchored OR full-bleed behind — pick one and commit.
- Trust / social-proof band right under hero: real-feeling logos, one specific stat ("£140M in property sold in 2025" not "10,000+ customers"), or a single short testimonial.
- Three to four feature or benefit sections, EACH visually distinct: one alternating image+text, one full-bleed feature with overlapping text, one card grid. Do not repeat the same layout twice.
- Testimonials with at least three quotes, named people, real-sounding companies, optional photo.
- Pricing or service tiers (if the niche calls for it) with one tier visually featured.
- FAQ accordion — at least 5 specific questions, no "What is X?" filler.
- Footer with newsletter signup, structured navigation columns, social, secondary CTA repeat, and a copyright line.{extras and chr(10) + "- Also include:" + extras}

Critical — every section must work as a still screenshot
- This site exists to be photographed. Each section is going to be cropped out and posted as a single carousel slide. Compose every section so it can stand alone as one image.
- Strong, clear focal point per section. No competing focal points in one viewport.
- Hierarchy reads instantly at thumbnail size: one dominant element, one supporting, then detail.
- Typography is large enough to read at 50% zoom in a 1080-wide phone preview.
- Negative space is part of the composition. Don't fill every pixel — leave breathing room around hero text and section headers.
- No mid-scroll states needed; no loaders, no half-revealed elements. Every section presents itself fully when scrolled to.
- No animations, transitions, parallax, or scroll effects. This site is a static visual reference, not a screen-recorded demo. Keep it clean and snappy — no motion, no scroll-triggered behaviour.
- Hover states are fine but not essential.

Build hygiene
- Use modern, accessible markup. Mobile-first. No layout shift on load. Test the layout at 375px, 768px, 1280px, 1440px — nothing should overlap or clip at any of those.
- Real copy throughout. NO lorem ipsum. NO generic SaaS phrases ("Build faster, ship better.", "Unlock your potential.", "The future of X.", "Welcome to {brand}", "Get started for free"). If copy starts to drift generic, rewrite it specific to {brand}'s actual offering.
- Real-feeling placeholder content: named team members, real-sounding testimonials with companies and roles, plausible product/service names, specific numbers, specific cities.
- One distinctive signature element this brand owns — a recurring shape, a navigation pattern, a colour-block treatment, a section marker. Something memorable that appears in multiple sections and ties the brand together.{notes}
"""
