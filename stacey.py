import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.patches as patches

def plot_stacey_matrix(df):
    fig, ax = plt.subplots(figsize=(8, 6))

    # Axes fixed from 0–9
    ax.set_xlim(0, 9)
    ax.set_ylim(0, 9)

    # Stacey zones — colors match your screenshot
    zones = [
        # (x_start, y_start, width, height, color, label)
        (0, 0, 3, 3, "#add8e6", "Stable"),             # Stable-Stable
        (3, 0, 3, 3, "#90ee90", "Complicated"),        # Complicated-Stable
        (6, 0, 2, 3, "#fffacd", "Complex"),            # Complex-Stable
        (8, 0, 1, 3, "#ffcccb", "Chaotic"),            # Chaotic-Stable

        (0, 3, 3, 3, "#add8e6", "Stable"),             # Stable-Complicated
        (3, 3, 3, 3, "#90ee90", "Complicated"),        # Complicated-Complicated
        (6, 3, 2, 3, "#fffacd", "Complex"),            # Complex-Complicated
        (8, 3, 1, 3, "#ffcccb", "Chaotic"),            # Chaotic-Complicated

        (0, 6, 3, 2, "#add8e6", "Stable"),             # Stable-Complex
        (3, 6, 3, 2, "#90ee90", "Complicated"),        # Complicated-Complex
        (6, 6, 2, 2, "#fffacd", "Complex"),            # Complex-Complex
        (8, 6, 1, 2, "#ffcccb", "Chaotic"),            # Chaotic-Complex

        (0, 8, 3, 1, "#add8e6", "Stable"),             # Stable-Chaotic
        (3, 8, 3, 1, "#90ee90", "Complicated"),        # Complicated-Chaotic
        (6, 8, 2, 1, "#fffacd", "Complex"),            # Complex-Chaotic
        (8, 8, 1, 1, "#ffcccb", "Chaotic"),            # Chaotic-Chaotic
    ]

    for (x, y, w, h, color, label) in zones:
        ax.add_patch(patches.Rectangle((x, y), w, h, linewidth=0, edgecolor=None, facecolor=color, alpha=0.4))

    # Scatter bubbles
    ax.scatter(df['Certainty_1to9'], df['Alignment_1to9'],
               s=df['MarketSize_Units'] * 0.05,
               alpha=0.6, edgecolors='black', linewidth=0.5)

    # Labels for each bubble
    for _, row in df.iterrows():
        ax.text(row['Certainty_1to9'], row['Alignment_1to9'], row['Country/Market'],
                fontsize=8, ha='center', va='center')

    ax.set_xlabel("CERTAINTY", fontsize=12)
    ax.set_ylabel("ALIGNMENT", fontsize=12)
    ax.set_title("Country Assessment", fontsize=14, pad=20)

    return fig
