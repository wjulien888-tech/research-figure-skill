"""Local SciencePlots contexts and size-preserving export. See ../LICENSE.md."""
from contextlib import contextmanager
from pathlib import Path
import math

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ft2font import FT2Font
import scienceplots  # Registers upstream styles; required, never silently substituted.


PROFILES = {
    "paper": (90.0, 62.0, 9.0),
    "report": (160.0, 100.0, 11.0),
    "slides": (240.0, 135.0, 18.0),
}


def positive(value, name):
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a positive number")
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise ValueError(f"{name} must be finite and positive")
    return number


def select_font(texts, family=None):
    """Choose a local font that covers all literal label characters, plus minus."""
    required = {ord(c) for t in texts for c in str(t) if not c.isspace()}
    required.add(0x2212)
    candidates = [family] if family else [
        "DejaVu Sans", "Noto Sans CJK SC", "Source Han Sans SC",
        "Microsoft YaHei", "PingFang SC", "Heiti SC", "Arial Unicode MS",
        "SimHei", "WenQuanYi Micro Hei",
    ]
    if not family:
        candidates += sorted({f.name for f in font_manager.fontManager.ttflist})
    for name in dict.fromkeys(candidates):
        try:
            path = font_manager.findfont(name, fallback_to_default=False)
            if required.issubset(FT2Font(path).get_charmap()):
                return name
        except (OSError, RuntimeError, ValueError):
            continue
    raise ValueError(
        "No installed font covers the labels. Set font_family to a suitable "
        "installed font (e.g. Noto Sans CJK SC for Chinese); labels were not translated."
    )


@contextmanager
def figure_context(profile="report", texts=(), styles=(), width_mm=None,
                   height_mm=None, font_size=None, font_family=None):
    if profile not in PROFILES:
        raise ValueError(f"Unknown profile: {profile}")
    width, height, size = PROFILES[profile]
    width = positive(width if width_mm is None else width_mm, "width_mm")
    height = positive(height if height_mm is None else height_mm, "height_mm")
    size = positive(size if font_size is None else font_size, "font_size")
    if not isinstance(styles, (list, tuple)):
        raise ValueError("styles must be a list of registered style names")
    for name in styles:
        if not isinstance(name, str) or name not in plt.style.available:
            raise ValueError(f"Unknown registered style: {name!r}")
    chosen_font = select_font(texts, font_family)
    settings = {
        "figure.figsize": (width / 25.4, height / 25.4),
        "font.size": size, "axes.labelsize": size,
        "axes.titlesize": size + 1, "legend.fontsize": size * 0.85,
        "xtick.labelsize": size * 0.85, "ytick.labelsize": size * 0.85,
        "font.family": [chosen_font], "axes.unicode_minus": True,
        "pdf.fonttype": 42, "svg.fonttype": "none",
        "savefig.facecolor": "white", "figure.facecolor": "white",
    }
    with plt.style.context(["science", *styles, "no-latex"]):
        with mpl.rc_context(settings):
            yield {"profile": profile, "styles": ["science", *styles, "no-latex"],
                   "font_family": chosen_font, "width_mm": width,
                   "height_mm": height, "font_size": size, "tex": False}


def save_figure(fig, base, formats=("png", "pdf", "svg"), dpi=300):
    """Save without tight cropping so requested physical dimensions survive."""
    if not formats or any(f not in {"png", "pdf", "svg"} for f in formats):
        raise ValueError("formats must contain png, pdf and/or svg")
    dpi = positive(dpi, "dpi")
    base = Path(base)
    base.parent.mkdir(parents=True, exist_ok=True)
    fig.canvas.draw()
    paths = []
    for extension in dict.fromkeys(formats):
        path = base.parent / (base.name + "." + extension)
        # bbox_inches=None alone inherits science's savefig.bbox='tight'.
        # Override that rcParam too, otherwise export silently changes size.
        with mpl.rc_context({"savefig.bbox": None}):
            fig.savefig(path, format=extension, dpi=dpi, bbox_inches=None)
        paths.append(path)
    return paths
