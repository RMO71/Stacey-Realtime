import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd

# Band edges on both axes
CUTS = [0, 3, 6, 8, 9]

# Zone colors (match your reference)
COL_YELLOW = "#FFE49C"  # Stable
COL_BLUE   = "#C6D7EE"  # Complicated (cross 3–6)
COL_GREEN  = "#CDEAC0"  # Complex (>=6 on either axis, except 8–9×8–9)
COL_RED    = "#FFC9C9"  # Chaotic (8–9 × 8–9 only)
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
    Stacey Matrix exactly as specified:

      - Axes fixed 0–9
      - Yellow:  0–3 × 0–3
      - Blue:    (X 3–6 over Y 0–6) UNION (Y 3–6 over X 0–6)
      - Green:   X 6–9 across all Y  AND  Y 6–9 across all X
                 (i.e., full 6–9 bands on both axes)
      - Red:     8–9 × 8–9 (overrides green in that square)

    Expects in df:
      'Country/Market', 'Certainty_1to9', 'Alignment_1to9', 'MarketSize_Units'
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    # Axis setup
    ax.set_xlim(0, 9); ax.set_ylim(0, 9)
    ax.set_xticks(range(0, 10)); ax.set_yticks(range(0, 10))

    # --- Background in correct stacking order ---
    # 1) Blue cross (3–6 band “between the axes” up to 6)
    _rect(ax, 3, 6, 0, 6, COL_BLUE)   # vertical arm
    _rect(ax, 0, 6, 3, 6, COL_BLUE)   # horizontal arm

    # 2) Green full bands (>=6 on either axis)
    _rect(ax, 6, 9, 0, 9, COL_GREEN)  # X >= 6, all Y
    _rect(ax, 0, 9, 6, 9, COL_GREEN)  # Y >= 6, all X

    # 3) Red cap (8–9 × 8–9 only)
    _rect(ax, 8, 9, 8, 9, COL_RED)

    # 4) Yellow bottom-left (0–3 × 0–3)
    _rect(ax, 0, 3, 0, 3, COL_YELLOW)

    # Band edge guides
    for c in CUTS[1:-1]:
        ax.axvline(c, linestyle="--", linewidth=0.8, alpha=0.6)
        ax.axhline(c, linestyle="--", linewidth=0.8, alpha=0.6)

    # --- Zone labels (smaller, colored tones) ---
    label_kw = dict(fontsize=12, alpha=0.8, ha="center", va="center", weight="bold")
    ax.text(1.5, 1.5, "STABLE",       color="#c99d00", **label_kw)  # yellow tone
    ax.text(4.5, 4.5, "COMPLICATED",  color="#2c4a7f", **label_kw)  # blue tone
    ax.text(7.0, 4.5, "COMPLEX",      color="#2a662a", **label_kw)  # green tone (X≥6 band)
    ax.text(4.5, 7.0, "COMPLEX",      color="#2a662a", **label_kw)  # green tone (Y≥6 band)
    ax.text(8.5, 8.5, "CHAOTIC",      color="#a12626", **label_kw)  # red tone

    # --- Bubbles ---
    xs = df["Certainty_1to9"].astype(float).clip(0, 9)
    ys = df["Alignment_1to9"].astype(float).clip(0, 9)
    ms = df["MarketSize_Units"].astype(float).clip(lower=0)
    labels = df["Country/Market"].astype(str).tolist()

    sizes = [max(50, math.sqrt(v) * size_scale) for v in ms]  # sqrt scaling + floor
    ax.scatter(xs, ys, s=sizes, alpha=0.65, edgecolors="black", linewidths=0.5)

    for x, y, lab in zip(xs, ys, labels):
        ax.text(x, y, lab, fontsize=8, ha="center", va="center")

    ax.set_xlabel("CERTAINTY")
    ax.set_ylabel("ALIGNMENT")
    ax.set_title(title, pad=18)
    ax.grid(True, linestyle=":", linewidth=0.5, alpha=0.35)

    return fig
