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
ALPHA = 0.35            # transparency

def _rect(ax, x0, x1, y0, y1, color, alpha=ALPHA):
    ax.add_patch(
        patches.Rectangle(
            (x0, y0), x1 - x0, y1 - y0,
            linewidth=0, facecolor=color, alpha=alpha
        )
    )

def _text(ax, x, y, txt, color="black", size=8, ha="center", va="bottom", weight=None):
    """Label with a thin white outline for readability."""
    t = ax.text(x, y, txt, fontsize=size, color=color, ha=ha, va=va, weight=weight)
    t.set_path_effects([
        pe.withStroke(linewidth=2.2, foreground="white", alpha=0.9)
    ])
    return t

def _name_hash_offset(name: str, low=-0.18, high=0.18) -> float:
    """Deterministic tiny x-offset based on the name to reduce stacking."""
    h = hashlib.md5(name.encode("utf-8")).hexdigest()
    v = int(h[:6], 16) / float(0xFFFFFF)  # 0..1
    return low + (high - low) * v

def make_stacey_figure(
    df: pd.DataFrame,
    x_low=None, x_high=None, y_low=None, y_high=None,  # kept for app compatibility (ignored)
    size_scale: float = 8,
    title: str = "Country Assessment",
):
    """
    Stacey Matrix (final):
      - Axes fixed 0–9
      - Yellow:  0–3 × 0–3
      - Blue:    (X 3–6 over Y 0–6)  UNION  (Y 3–6 over X 0–6)
      - Green:   X 6–9 across all Y  AND  Y 6–9 across all X
      - Red:     7–9 × 7–9 (drawn last to fully overlay green)
      - Overlap handling:
          * Bubbles sharing the same (x,y) are spread on a ring, each label offset radially
          * Single points get a small deterministic x-jitter for labels
          * Labels have white outline + leader lines when offset
    Expects columns:
      'Country/Market', 'Certainty_1to9', 'Alignment_1to9', 'MarketSize_Units'
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    # Axes and ticks
    ax.set_xlim(0, 9); ax.set_ylim(0, 9)
    ax.set_xticks(range(0, 10)); ax.set_yticks(range(0, 10))

    # --- Background zones (stacking order matters) ---
    # 1) Blue cross (3–6)
    _rect(ax, 3, 6, 0, 6, COL_BLUE)   # vertical arm
    _rect(ax, 0, 6, 3, 6, COL_BLUE)   # horizontal arm
    # 2) Green areas (>=6 on either axis)
    _rect(ax, 6, 9, 0, 9, COL_GREEN)  # X >= 6
    _rect(ax, 0, 9, 6, 9, COL_GREEN)  # Y >= 6
    # 3) Red chaotic zone (EXPANDED): 7–9 × 7–9 — draw LAST
    _rect(ax, 7, 9, 7, 9, COL_RED)
    # 4) Yellow stable zone
    _rect(ax, 0, 3, 0, 3, COL_YELLOW)

    # --- Zone labels (smaller, color-toned) ---
    label_kw = dict(fontsize=12, alpha=0.8, ha="center", va="center", weight="bold")
    _text(ax, 1.5, 1.5, "STABLE",      color="#c99d00", **label_kw)
    _text(ax, 4.5, 4.5, "COMPLICATED", color="#2c4a7f", **label_kw)
    _text(ax, 7.0, 4.5, "COMPLEX",     color="#2a662a", **label_kw)  # X≥6 band
    _text(ax, 4.5, 7.0, "COMPLEX",     color="#2a662a", **label_kw)  # Y≥6 band
    _text(ax, 8.0, 8.0, "CHAOTIC",     color="#a12626", **label_kw)  # 7–9 zone

    # --- Data in a convenient frame ---
    xs = df["Certainty_1to9"].astype(float).clip(0, 9).values
    ys = df["Alignment_1to9"].astype(float).clip(0, 9).values
    ms = df["MarketSize_Units"].astype(float).clip(lower=0).values
    labs = df["Country/Market"].astype(str).values

    base = pd.DataFrame({"x": xs, "y": ys, "m": ms, "lab": labs})

    # Group exact (x,y) duplicates
    groups = base.groupby(["x", "y"], sort=False)

    # Parameters
    R_MIN, R_MAX = 0.14, 0.26         # ring radius (axis units) for duplicates
    LABEL_PUSH = 0.28                 # extra radial push for label position
    for (x0, y0), g in groups:
        k = len(g)
        r = R_MIN if k == 1 else min(R_MAX, R_MIN + 0.04 * (k - 1))

        if k == 1:
            row = g.iloc[0]
            size = max(50, math.sqrt(row["m"]) * size_scale)
            ax.scatter([x0], [y0], s=[size], alpha=0.65, edgecolors="black", linewidths=0.5)
            # tiny deterministic x jitter for label to avoid stacks across neighbors
            jx = _name_hash_offset(str(row["lab"]), -0.14, 0.14)
            _text(ax, x0 + jx, y0 + 0.22, str(row["lab"]))
            continue

        # Spread duplicates evenly around the point; labels offset further out with leader lines
        angles = [2 * math.pi * i / k for i in range(k)]
        for ang, (_, row) in zip(angles, g.iterrows()):
            x = x0 + r * math.cos(ang)
            y = y0 + r * math.sin(ang)
            x = max(0, min(9, x)); y = max(0, min(9, y))

            size = max(50, math.sqrt(row["m"]) * size_scale)
            ax.scatter([x], [y], s=[size], alpha=0.65, edgecolors="black", linewidths=0.5)

            # Label a bit farther out along the same angle
            lx = x0 + (r + LABEL_PUSH) * math.cos(ang)
            ly = y0 + (r + LABEL_PUSH) * math.sin(ang)
            lx = max(0, min(9, lx)); ly = max(0, min(9, ly))

            # Leader line
            ax.plot([x, lx], [y, ly], linewidth=0.6, alpha=0.6, color="black")

            _text(ax, lx, ly, str(row["lab"]), ha="center", va="center")

    # Axes labels/title and pale dotted grid
    ax.set_xlabel("CERTAINTY")
    ax.set_ylabel("ALIGNMENT")
    ax.set_title(title, pad=18)
    ax.grid(True, linestyle=":", linewidth=0.5, alpha=0.35)

    return fig
