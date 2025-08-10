from math import sqrt
import matplotlib.pyplot as plt

def make_stacey_figure(df, x_col="Certainty_1to9", y_col="Alignment_1to9",
                       size_col="MarketSize_Units", label_col="Country/Market",
                       x_min=1, x_max=9, y_min=1, y_max=9,
                       x_low=3, x_high=7, y_low=3, y_high=7,
                       size_scale=8, title="Stacey Matrix (1–9) – Certainty vs Alignment"):
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.set_xlim(x_min, x_max); ax.set_ylim(y_min, y_max)
    ax.set_xlabel("Certainty (1 → 9)")
    ax.set_ylabel("Alignment (1 → 9)")
    ax.set_title(title)
    ax.grid(True, linestyle="--", linewidth=0.5)
    ax.axvline(x_low, linestyle="--", linewidth=0.8)
    ax.axvline(x_high, linestyle="--", linewidth=0.8)
    ax.axhline(y_low, linestyle="--", linewidth=0.8)
    ax.axhline(y_high, linestyle="--", linewidth=0.8)
    ax.text(x_min+0.2, y_max-0.5, "Complex", fontsize=10)
    ax.text(x_high+0.2, y_max-0.5, "Aligned & Certain", fontsize=10)
    ax.text(x_min+0.2, y_min+0.1, "Chaotic", fontsize=10)
    ax.text(x_high+0.2, y_min+0.1, "Complicated", fontsize=10)
    for _, row in df.iterrows():
        try:
            x = float(row[x_col]); y = float(row[y_col])
            size = max(50, sqrt(max(float(row[size_col]), 0)) * size_scale)
            ax.scatter([x], [y], s=size, alpha=0.6, edgecolors="black", linewidths=0.5)
            ax.annotate(str(row[label_col]), (x, y), xytext=(5, 5), textcoords="offset points", fontsize=9)
        except Exception:
            continue
    return fig
