import math
import hashlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as pe
import pandas as pd

# Zone colors
COL_YELLOW = "#FFE49C"  # Stable
COL_BLUE   = "#C6D7EE"  # Complicated (3–6 cross)
COL_GREEN  = "#CDEAC0"  # Complex (>=6 on either axis)
COL_RED    = "#FFC9C9"  # Chaotic (7–9 × 7–9)
ALPHA = 0.35

def _rect(ax, x0, x1, y0, y1, color, alpha=ALPHA):
    ax.add_patch(patches.Rectangle((x0, y0), x1 - x0, y1 - y0,
                                   linewidth=0, facecolor=color, alpha=alpha))

def _outline_text(ax, x, y, txt, color="black", size=8, ha="center", va="center", weight=None):
    t = ax.text(x, y, txt, fontsize=size, color=color, ha=ha, va=va, weight=weight)
    t.set_path_effects([pe.withStroke(linewidth=2.4, foreground="white", alpha=0.95)])
    return t

def _hash_angle(name: str) -> float:
    """Deterministic 0..2π angle from a name (for stable label directions)."""
    h = hashlib.sha1(name.encode("utf-8")).hexdigest()
    v = int(h[:8], 16) / float(0xFFFFFFFF)
    return 2 * math.pi * v

def _keep_inside(x, y, pad=0.25):
    """Clamp a point into [0..9]x[0..9] with a small padding."""
    return max(pad, min(9 - pad, x)), max(pad, min(9 - pad, y))

def make_stacey_figure(
    df: pd.DataFrame,
    x_low=None, x_high=None, y_low=None, y_high=None,  # kept for app compatibility (ignored)
    size_scale: float = 8,
    title: str = "Country Assessment",
):
    """
    Stacey Matrix with zones + distance labels and leader lines.

    Zones:
      - Yellow:  0–3 × 0–3
      - Blue:    (X 3–6 over Y 0–6) UNION (Y 3–6 over X 0–6)
      - Green:   X 6–9 across all Y AND Y 6–9 across all X
      - Red:     7–9 × 7–9 (drawn last to overlay green)

    Labels:
      - Every label is placed at a CLEAR distance from its bubble
      - Direction is deterministic by country name (stable layout)
      - Leader line drawn from bubble to label
      - Overlapping bubbles at the same (x,y) are fanned on a small ring
        and labels are placed even farther out along the same angles
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    # Axes
    ax.set_xlim(0, 9); ax.set_ylim(0, 9)
    ax.set_xticks(range(0, 10)); ax.set_yticks(range(0, 10))

    # Background zones (stacking order)
    _rect(ax, 3, 6, 0, 6, COL_BLUE)   # blue cross
    _rect(ax, 0, 6, 3, 6, COL_BLUE)
    _rect(ax, 6, 9, 0, 9, COL_GREEN)  # green bands
    _rect(ax, 0, 9, 6, 9, COL_GREEN)
    _rect(ax, 7, 9, 7, 9, COL_RED)    # chaotic 7–9 × 7–9
    _rect(ax, 0, 3, 0, 3, COL_YELLOW) # stable

    # Zone labels (smaller, toned)
    label_kw = dict(fontsize=12, alpha=0.8, ha="center", va="center", weight="bold")
    _outline_text(ax, 1.5, 1.5, "STABLE",      color="#c99d00", **label_kw)
    _outline_text(ax, 4.5, 4.5, "COMPLICATED", color="#2c4a7f", **label_kw)
    _outline_text(ax, 7.0, 4.5, "COMPLEX",     color="#2a662a", **label_kw)
    _outline_text(ax, 4.5, 7.0, "COMPLEX",     color="#2a662a", **label_kw)
    _outline_text(ax, 8.0, 8.0, "CHAOTIC",     color="#a12626", **label_kw)

    # Data
    xs = df["Certainty_1to9"].astype(float).clip(0, 9).values
    ys = df["Alignment_1to9"].astype(float).clip(0, 9).values
    ms = df["MarketSize_Units"].astype(float).clip(lower=0).values
    labs = df["Country/Market"].astype(str).values
    data = pd.DataFrame({"x": xs, "y": ys, "m": ms, "lab": labs})

    groups = data.groupby(["x", "y"], sort=False)

    # Parameters
    R_BUBBLE_MIN, R_BUBBLE_MAX = 0.14, 0.26     # ring radius for bubble fanning
    LABEL_DISTANCE_SINGLE      = 0.55           # distance from bubble for singles
    LABEL_DISTANCE_GROUP_EXTRA = 0.40           # extra distance beyond the ring for groups
    for (x0, y0), g in groups:
        k = len(g)
        # grow ring with group size
        r = R_BUBBLE_MIN if k == 1 else min(R_BUBBLE_MAX, R_BUBBLE_MIN + 0.05 * (k - 1))

        if k == 1:
            row = g.iloc[0]
            size = max(50, math.sqrt(row["m"]) * size_scale)
            ax.scatter([x0], [y0], s=[size], alpha=0.65, edgecolors="black", linewidths=0.5)

            ang = _hash_angle(row["lab"])
            lx = x0 + LABEL_DISTANCE_SINGLE * math.cos(ang)
            ly = y0 + LABEL_DISTANCE_SINGLE * math.sin(ang)
            lx, ly = _keep_inside(lx, ly)

            # leader
            ax.plot([x0, lx], [y0, ly], linewidth=0.7, alpha=0.65, color="black")
            _outline_text(ax, lx, ly, row["lab"])
            continue

        # Fan bubbles on a ring; labels even farther out
        angles = [2 * math.pi * i / k for i in range(k)]
        for ang, (_, row) in zip(angles, g.iterrows()):
            bx = x0 + r * math.cos(ang)
            by = y0 + r * math.sin(ang)
            bx, by = _keep_inside(bx, by)

            size = max(50, math.sqrt(row["m"]) * size_scale)
            ax.scatter([bx], [by], s=[size], alpha=0.65, edgecolors="black", linewidths=0.5)

            # place label further along the same ray
            lx = x0 + (r + LABEL_DISTANCE_GROUP_EXTRA) * math.cos(ang)
            ly = y0 + (r + LABEL_DISTANCE_GROUP_EXTRA) * math.sin(ang)
            lx, ly = _keep_inside(lx, ly)

            ax.plot([bx, lx], [by, ly], linewidth=0.7, alpha=0.65, color="black")
            _outline_text(ax, lx, ly, row["lab"])

    # Axes labels/title and pale dotted grid
    ax.set_xlabel("CERTAINTY")
    ax.set_ylabel("ALIGNMENT")
    ax.set_title(title, pad=18)
    ax.grid(True, linestyle=":", linewidth=0.5, alpha=0.35)

    return fig
