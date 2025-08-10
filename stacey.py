import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd

# Band edges on both axes
CUTS = [0, 3, 6, 8, 9]

# Zone colors
COL_YELLOW = "#FFE49C"  # Stable
COL_BLUE   = "#C6D7EE"  # Complicated (cross 3–6)
COL_GREEN  = "#CDEAC0"  # Complex (>=6 on either axis, except 8–9×8–9)
COL_RED    = "#FFC9C9"  # Chaotic (8–9 × 8–9)
ALPHA = 0.35

def _rect(ax, x0, x1, y0, y1, color, alpha=ALPHA):
    ax.add_patch(
        patches.Rectangle(
            (x0, y0), x1 - x0, y1 - y0,
            linewidth=0, facecolor=color, alpha=alpha
        )
    )

def make_stacey_figure(
    df: pd.DataFrame,
    x_low=None, x_high=None, y_low=None, y_high=None,  # kept for app compatibility (ignored)
    size_scale: float = 8,
    title: str = "Country Assessment",
):
    """
    Stacey Matrix layout:
      - Yellow:  0–3 × 0–3
      - Blue:    (X 3–6 over Y 0–6) UNION (Y 3–6 over X 0–6)
      - Green:   X 6–9 across all Y  AND  Y 6–9 across all X
      - Red:     8–9 × 8–9 (overrides green there)

    Expects columns:
      'Country/Market', 'Certainty_1to9', 'Alignment_1to9', 'MarketSize_Units'
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    # Axes and ticks
    ax.set_xlim(0, 9); ax.set_ylim(0, 9)
    ax.set_xticks(range(0, 10)); ax.set_yticks(range(0, 10))

    # --- Background zones (stack order matters) ---
    # Blue cross (3–6, up to 6 on the other axis)
    _rect(ax, 3, 6, 0, 6, COL_BLUE)   # vertical arm
    _rect(ax, 0, 6, 3, 6, COL_BLUE)   # horizontal arm

    # Green full bands (>=6 on either axis)
    _rect(ax, 6, 9, 0, 9, COL_GREEN)  # X >= 6
    _rect(ax, 0, 9, 6, 9, COL_GREEN)  # Y >= 6

    # Red cap (top-right)
    _rect(ax, 8, 9, 8, 9, COL_RED)

    # Yellow bottom-left
    _rect(ax, 0, 3, 0, 3, COL_YELLOW)

    # --- Zone labels (smaller, color-toned) ---
    label_kw = dict(fontsize=12, alpha=0.8, ha="center", va="center", weight="bold")
    ax.text(1.5, 1.5, "STABLE",       color="#c99d00", **label_kw)  # yellow tone
    ax.text(4.5, 4.5, "COMPLICATED",  color="#2c4a7f", **label_kw)  # blue tone
    ax.text(7.0, 4.5, "COMPLEX",      color="#2a662a", **label_kw)  # green tone (X≥6 band)
    ax.text(4.5, 7.0, "COMPLEX",      color="#2a662a", **label_kw)  # green tone (Y≥6 band)
    ax.text(8.5, 8.5, "CHAOTIC",      color="#a12626", **label_kw)  # red tone

    # --- Data & bubbles ---
    xs = df["Certainty_1to9"].astype(float).clip(0, 9)
    ys = df["Alignment_1to9"].astype(float).clip(0, 9)
    ms = df["MarketSize_Units"].astype(float).clip(lower=0)
    labels = df["Country/Market"].astype(str).tolist()

    # Bubble sizes (sqrt scaling + floor)
    sizes = [max(50, math.sqrt(v) * size_scale) for v in ms]
    ax.scatter(xs, ys, s=sizes, alpha=0.65, edgecolors="black", linewidths=0.5)

    # Country names ABOVE bubbles
    for x, y, lab in zip(xs, ys, labels):
        ax.text(x, y + 0.22, lab, fontsize=8, ha="center", va="bottom")

    # Axes labels/title
    ax.set_xlabel("CERTAINTY")
    ax.set_ylabel("ALIGNMENT")
    ax.set_title(title, pad=18)

    # Pale dotted grid only (no bold band lines)
    ax.grid(True, linestyle=":", linewidth=0.5, alpha=0.35)

    return fig
