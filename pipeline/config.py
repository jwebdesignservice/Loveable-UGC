"""Paths, sizes, and tunables shared across the pipeline."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
SITES_DIR = DATA_DIR / "site-previews"
CAROUSELS_DIR = DATA_DIR / "carousels"
ASSETS_DIR = ROOT / "assets"
STATE_FILE = DATA_DIR / "state.json"

SIZE_9X16 = (1080, 1920)
SIZE_1X1 = (1080, 1080)

PAPER = (236, 232, 225)
INK = (22, 21, 19)
MUTED = (107, 102, 96)
PILL_BG = (17, 17, 17)
PILL_FG = (255, 255, 255)

FONT_REG = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"

CAROUSELS_PER_DESIGN = 12
PILLARS = ["site-previews", "one-prompt-site", "one-shot-revamp",
           "how-to", "common-mistakes"]


def ensure_dirs() -> None:
    for d in (DATA_DIR, SITES_DIR, CAROUSELS_DIR, ASSETS_DIR):
        d.mkdir(parents=True, exist_ok=True)
