"""Content I/O for the pipeline.

The orchestrator (Claude Code) writes carousel scripts to a JSON file and
the pipeline reads them. No LLM calls here — the renderer is purely
deterministic.

Stub data is kept for offline smoke-testing only.
"""
from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CarouselScript:
    pillar: str
    hook: str
    caption: str
    hashtags: list[str]


CONTENT_JSON_SCHEMA = """The orchestrator should write a file like:

{
  "carousels": [
    {
      "pillar": "site-previews",
      "hook": "i built this site with lovable in 3 days.",
      "caption": "lovable did 90 percent of this. small tweaks only.",
      "hashtags": ["#lovable", "#webdesign", "#buildinpublic"]
    },
    {
      "pillar": "one-prompt-site",
      "hook": "lovable made this from one prompt.",
      "caption": "the prompt is 18 words. that's it.",
      "hashtags": ["#lovable", "#aitools"]
    }
  ]
}

Save it as data/site-previews/<slug>/content.json. The pipeline's render-batch
command reads it and renders every carousel in the array.
"""


def load_from_json(path: Path) -> list[CarouselScript]:
    """Load carousel scripts from a JSON file written by the orchestrator."""
    raw = json.loads(Path(path).read_text())
    return [CarouselScript(**c) for c in raw["carousels"]]


def stub_carousels(n: int = 4) -> list[CarouselScript]:
    """Offline fallback for smoke-testing the renderer without an orchestrator."""
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
