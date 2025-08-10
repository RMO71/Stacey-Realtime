import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd

# Band edges used on both axes
CUTS = [0, 3, 6, 8, 9]

# Colors (tuned to your reference)
COL_YELLOW = "#FFE49C"  # 0–3 × 0–3
COL_BLUE   = "#C6D7EE"  # 3–6 cross
COL_GREEN  = "#CDEAC0"  # full 6–9 bands (both axes)
COL_RED    = "#FFC9C9"  # 8–9 × 8–9 only
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
      - Yellow: 0–3 on X and 0–3 on Y
      - Blue:   (X 3–6 across Y 0–6) UNION (Y 3–6 across X 0–6)
      - Green:  X 6–9 across Y 0–9  AND  Y 6–9 across X 0–9  (full bands)
      - Red:    8–9 × 8–9 only (overrides green there)
    """

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlim(0, 9); ax.set_ylim(0, 9)
    ax.set_xticks(range(0, 10)); ax.set_yticks(range(0, 10))

    # --- Draw zones in the right stacking order ---
    # 1) Blue cross first (so green can overwrite above/beyond 6)
    _rect(ax, 3, 6, 0, 6, COL_BLUE)  # vertical arm: X 3–6 over Y 0–6
    _rect(ax, 0, 6, 3, 6, COL_BLUE)  # horizontal arm: Y 3–6 over X 0–6

    # 2) Green full bands (6–9 on either axis)
    _rect(ax, 6, 9, 0, 9, COL_GREEN)  # X >= 6 across all Y
    _rect(ax, 0, 9, 6, 9, COL_GREEN)  # Y >= 6 across all X

    # 3) Red cap: only where both axes are 8–9
    _rect(ax, 8, 9, 8, 9, COL_RED)

    # 4) Yellow bottom-left (doesn't overlap blue)
    _rect(ax, 0, 3, 0, 3, COL_YELLOW)

    # Guideline grid at band edges
    for c in CUTS[1:-1]:
        ax.axvline(c, linestyle="--", linewidth=0.8, alpha=0.6)
        ax.axhline(c, linestyle="--", linewidth=0.8, alpha=0.6)

    # --- Plot bubbles ---
    xs = df["Certainty_1to9"].astype(float).clip(0, 9)
    ys = df["Alignment_1to9"].astype(float).clip(0, 9)
    ms = df["MarketSize_Units"].astype(float).clip(lower=0)
    labels = df["Country/Market"].astype(str).tolist()

    sizes = [max(50, math.sqrt(v) * size_scale) for v in ms]
    ax.scatter(xs, ys, s=sizes, alpha=0.65, edgecolors="black", linewidths=0.5)

    for x, y, lab in zip(xs, ys, labels):
        ax.text(x, y, lab, fontsize=8, ha="center", va="center")

    ax.set_xlabel("CERTAINTY")
    ax.set_ylabel("ALIGNMENT")
    ax.set_title(title, pad=18)
    ax.grid(True, linestyle=":", linewidth=0.5, alpha=0.35)

    return fig
