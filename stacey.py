import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def make_stacey_figure(
    df,
    x_low=None, x_high=None, y_low=None, y_high=None,  # accepted for compatibility; ignored
    size_scale=8,
    title="Country Assessment"
):
    """
    Draw a Stacey Matrix with fixed 0–9 axes and zones:
      0–3 Stable, 3–6 Complicated, 6–8 Complex, 8–9 Chaotic (both axes).
    Expected columns in df: 'Country/Market', 'Certainty_1to9', 'Alignment_1to9', 'MarketSize_Units'
    """
    # Fixed cuts for both axes
    cuts = [0, 3, 6, 8, 9]

    # Colors for bands (Stable, Complicated, Complex, Chaotic)
    band_colors = {
        0: "#cfe3ff",  # Stable (light blue)
        1: "#d9f2d9",  # Complicated (light green)
        2: "#fff3bf",  # Complex (light yellow)
        3: "#ffc9c9",  # Chaotic (light red)
    }

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlim(0, 9)
    ax.set_ylim(0, 9)

    # Draw 16 rectangles (4x4 grid), color by Y band for a look close to your example
    for ix in range(4):
        for iy in range(4):
            x0, x1 = cuts[ix], cuts[ix + 1]
            y0, y1 = cuts[iy], cuts[iy + 1]
            color = band_colors[iy]  # color by Y band (matches the reference look)
            ax.add_patch(
                patches.Rectangle(
                    (x0, y0),
                    x1 - x0,
                    y1 - y0,
                    linewidth=0,
                    facecolor=color,
                    alpha=0.35,
                )
            )

    # Grid lines at the cuts to make the zones crisp
    for c in cuts[1:-1]:
        ax.axvline(c, linestyle="--", linewidth=0.8, alpha=0.6)
        ax.axhline(c, linestyle="--", linewidth=0.8, alpha=0.6)

    # Scatter bubbles (sqrt scaling)
    xs = df["Certainty_1to9"].astype(float)
    ys = df["Alignment_1to9"].astype(float)
    ms = df["MarketSize_Units"].astype(float).clip(lower=0)
    sizes = [max(50, math.sqrt(v) * size_scale) for v in ms]

    sc = ax.scatter(xs, ys, s=sizes, alpha=0.65, edgecolors="black", linewidths=0.5)

    # Labels
    labels = df["Country/Market"].astype(str).tolist()
    for x, y, lab in zip(xs, ys, labels):
        ax.text(x, y, lab, fontsize=8, ha="center", va="center")

    # Axes & title
    ax.set_xlabel("CERTAINTY")
    ax.set_ylabel("ALIGNMENT")
    ax.set_title(title, pad=18)
    ax.grid(True, linestyle=":", linewidth=0.5, alpha=0.4)

    # Tick marks at 0..9
    ax.set_xticks(range(0, 10))
    ax.set_yticks(range(0, 10))

    return fig
