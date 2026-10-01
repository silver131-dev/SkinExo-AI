#!/usr/bin/env python3
"""Generate the public v0.3 architecture status figure without changing F2 data."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "submission/figures/fig09_skinexo_platform_architecture.png"


def main() -> None:
    stages = [
        ("Public EV studies", "GEO/SRA + study metadata"),
        ("Context normalization", "source · recipient · dose · time"),
        ("Reproducible analysis", "QC · DE · ranked enrichment"),
        ("Response Atlas", "339 frozen components × 3 contexts"),
        ("Component-aware evidence", "direction · NES · FDR · null/missingness"),
        ("Reliability", "separate design and evidence dimensions"),
        ("Retrieval R1", "interpretable mask-aware context similarity"),
        ("Explorer A1", "interactive offline evidence inspection"),
    ]
    fig, ax = plt.subplots(figsize=(11, 14), constrained_layout=True)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 15)
    ax.axis("off")
    fig.suptitle("SkinExo-AI Platform Architecture", fontsize=24, fontweight="bold")
    ax.text(
        5,
        14.55,
        "Context-aware evidence representation; predictive AI is not implemented",
        ha="center",
        fontsize=12,
        color="#455465",
    )
    ys = [13.3, 11.65, 10.0, 8.35, 6.7, 5.05, 3.4, 1.75]
    for index, ((title, subtitle), y) in enumerate(zip(stages, ys)):
        ax.add_patch(
            FancyBboxPatch(
                (1.35, y - 0.55),
                7.3,
                1.05,
                boxstyle="round,pad=0.02,rounding_size=0.08",
                facecolor="#D7EAF5",
                edgecolor="#2878A5",
                linewidth=2,
            )
        )
        ax.text(5, y + 0.13, title, ha="center", fontsize=15, fontweight="bold")
        ax.text(5, y - 0.2, subtitle, ha="center", fontsize=10.5, color="#425466")
        ax.text(
            8.95,
            y,
            "IMPLEMENTED",
            ha="left",
            va="center",
            fontsize=10,
            fontweight="bold",
            color="#2878A5",
        )
        if index < len(stages) - 1:
            ax.add_patch(
                FancyArrowPatch(
                    (5, y - 0.57),
                    (5, ys[index + 1] + 0.57),
                    arrowstyle="-|>",
                    mutation_scale=18,
                    color="#65717E",
                    linewidth=1.7,
                )
            )
    ax.text(
        5,
        0.62,
        "v0.3 boundary: evidence engine, Atlas, reliability, R1 retrieval, and A1 Explorer are implemented.",
        ha="center",
        fontsize=10.5,
        color="#384554",
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
