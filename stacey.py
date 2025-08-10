import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd

CUTS = [0, 3, 6, 8, 9]

COL_YELLOW = "#FFE49C"
COL_BLUE   = "#C6D7EE"
COL_GREEN  = "#CDEAC0"
COL_RED    = "#FFC9C9"
ALPHA = 0.35

def make_stacey_figure(
    df: pd.DataFrame,
    x_low=None, x_high=None, y_low=None, y_high=None,  # kept for app compatibility
    size_scale: float = 8,
    title: str = "Country Assessment",
):
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlim(0, 9)
    ax.set_ylim(0, 9)
    ax.set_xticks(range(0, 10))
    ax.set_yticks(range(0, 10))

    # Color only the diagonal zones
    zones = [
        (0, 3, 0, 3, COL_YELLOW),
        (3, 6, 3, 6, COL_BLUE),
        (6, 8, 6, 8, COL_GREEN),
        (8, 9, 8, 9, COL_RED)
    ]

    for x0, x1, y0, y1, color in zones:
        ax.add_patch(
            patches.Rectangle(
                (x0, y0), x1 - x0, y1 - y0,
                linewidth=0, facecolor=color, alpha=ALPHA
            )
        )

    # Draw gridlines at the band edges
    for c in CUTS[1:-1]:
        ax.axvline(c, linestyle="--", linewidth=0.8, alpha=0.6)
        ax.axhline(c, linestyle="--", linewidth=0.8, alpha=0.6)

    # Data
    xs = df["Certainty_1to9"].astype(float).clip(0, 9)
    ys = df["Alignment_1to9"].astype(float).clip(0, 9)
    ms = df["MarketSize_Units"].astype(float).clip(lower=0)
    labels = df["Country/Market"].astype(str).tolist()

    # Bubble sizes (sqrt scaling)
    sizes = [max(50, math.sqrt(v) * size_scale) for v in ms]

    ax.scatter(xs, ys, s=sizes, alpha=0.65, edgecolors="black", linewidths=0.5)

    # Add labels centered on bubbles
    for x, y, lab in zip(xs, ys, labels):
        ax.text(x, y, lab, fontsize=8, ha="center", va="center")

    ax.set_xlabel("CERTAINTY")
    ax.set_ylabel("ALIGNMENT")
    ax.set_title(title, pad=18)
    ax.grid(True, linestyle=":", linewidth=0.5, alpha=0.35)

    return fig
