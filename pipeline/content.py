"""Content generator. Calls Claude to produce N carousel variations
(hook + caption + hashtags) off a single Lovable site.

Hooks are UGC, lowercase, conversational. They mention Lovable concretely.
"""
from __future__ import annotations
import json
import os
from dataclasses import dataclass
from typing import Optional

from anthropic import Anthropic

MODEL = "claude-opus-4-7"


@dataclass
class CarouselScript:
    pillar: str
    hook: str
    caption: str
    hashtags: list[str]


SYSTEM = """You write short-form UGC carousel content for an account that
showcases websites built with Lovable (lovable.dev). The format is image
carousels for Instagram and TikTok.

Voice:
- lowercase, conversational, no marketing-speak
- short hooks (under 10 words) that pattern-interrupt
- caption is 1-3 short sentences max
- never sales-y, never "swipe right" or "link in bio" energy
- always mention Lovable concretely (e.g. "i built this with lovable", "this is what lovable made", "lovable did this in one prompt")
- treat the reader like a builder friend, not a customer

For each carousel you generate, the slides are:
- slide 1: the site hero with the hook overlaid
- slides 2..N: clean site screenshots, no text
The hook is the only writing on slide 1. The site does the rest.
"""

USER_TEMPLATE = """Site context:
- niche: {niche}
- brand: {brand}
- description: {description}
- the prompt I gave Lovable: "{prompt}"
- live url: {url}

Produce {n} different carousels off this one site. Vary the angle:
- some can be "i built this in X" framing
- some can be "Lovable did this from one prompt"
- some can be "look how clean this came out"
- some can be a numeric flex ("4 minutes", "12 words", "first try")
- some can be question hooks ("can you believe lovable made this?")

Return JSON only, no prose, matching this shape:
{{
  "carousels": [
    {{
      "pillar": "site-previews" | "one-prompt-site",
      "hook": "short hook for slide 1",
      "caption": "post caption, 1-3 sentences",
      "hashtags": ["#lovable", "#webdesign", ...]
    }}
  ]
}}
"""


def generate_carousels(*, niche: str, brand: str, description: str,
                      prompt: str, url: str, n: int = 4) -> list[CarouselScript]:
    """Generate `n` carousel variations for one site."""
    client = Anthropic()
    msg = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=SYSTEM,
        messages=[{
            "role": "user",
            "content": USER_TEMPLATE.format(
                niche=niche, brand=brand, description=description,
                prompt=prompt, url=url, n=n,
            ),
        }],
    )
    text = "".join(b.text for b in msg.content if b.type == "text")
    text = _strip_fences(text)
    data = json.loads(text)
    return [CarouselScript(**c) for c in data["carousels"]]


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[: text.rfind("```")]
    return text.strip()


def stub_carousels(n: int = 4) -> list[CarouselScript]:
    """Offline fallback for testing without an API key. Stable, varied."""
    base = [
        ("site-previews", "i built this with lovable in 3 days.",
         "lovable did 90 percent of this. one prompt, then small tweaks.",
         ["#lovable", "#webdesign", "#buildinpublic"]),
        ("one-prompt-site", "lovable made this from one prompt.",
         "the prompt is 18 words. that's it.",
         ["#lovable", "#aitools", "#nocode"]),
        ("site-previews", "can you believe lovable did this?",
         "every section here is from a single prompt. wild.",
         ["#lovable", "#webdesign", "#designinspo"]),
        ("one-prompt-site", "12 words. one full site.",
         "this is what lovable shipped on the first try.",
         ["#lovable", "#vibecoding", "#indiehackers"]),
        ("site-previews", "4 minutes inside lovable.",
         "no figma. no code. just a prompt and some patience.",
         ["#lovable", "#webdesign", "#nocode"]),
        ("one-prompt-site", "lovable cooked.",
         "one prompt and it gave me this entire landing page.",
         ["#lovable", "#aitools", "#design"]),
    ]
    out = []
    for i in range(n):
        p, h, c, t = base[i % len(base)]
        out.append(CarouselScript(pillar=p, hook=h, caption=c, hashtags=t))
    return out


def have_api_key() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))
