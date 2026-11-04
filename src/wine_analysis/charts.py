"""Static charts for the README (matplotlib, light theme).

Colours come from one fixed categorical order so a series keeps its colour in
every chart. Every multi-series chart is also direct-labelled, so no chart
depends on colour alone.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#e4e3df"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]  # blue, orange, aqua
HIGHLIGHT = SERIES[0]
MUTED = "#b9b8b2"

plt.rcParams.update(
    {
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "axes.edgecolor": GRID,
        "axes.labelcolor": INK_2,
        "axes.titlecolor": INK,
        "axes.titleweight": "bold",
        "axes.titlesize": 13,
        "axes.titlelocation": "left",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "xtick.color": INK_2,
        "ytick.color": INK_2,
        "font.size": 10,
        "savefig.dpi": 160,
        "savefig.bbox": "tight",
    }
)


def _finish(fig, path: Path) -> None:
    fig.savefig(path)
    plt.close(fig)


def top_producers_bar(top: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 3.6))
    df = top.iloc[::-1]
    ax.barh(df["Country"], df["Production_mHL"], color=HIGHLIGHT, height=0.6)
    for y, v in enumerate(df["Production_mHL"]):
        ax.text(v + 0.3, y, f"{v:g}", va="center", color=INK)
    ax.set_xlabel("Red wine production (million hectolitres)")
    ax.set_title("Top 5 red wine producers")
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    _finish(fig, path)


def usa_colour_lines(usa_long: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.5, 4))
    for colour, c in zip(["White", "Red", "Rosé"], SERIES):
        g = usa_long[usa_long["Colour"] == colour].sort_values("Year")
        ax.plot(g["Year"], g["Production_mHL"], color=c, linewidth=2)
        ax.text(g["Year"].iloc[-1] + 0.3, g["Production_mHL"].iloc[-1], colour,
                va="center", color=INK)
    ax.set_ylabel("Million hectolitres")
    ax.set_title("U.S. wine production by colour, 2000 to 2021")
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_xlim(usa_long["Year"].min(), usa_long["Year"].max() + 2)
    ax.set_ylim(bottom=0)
    _finish(fig, path)


def price_bar(prices: pd.DataFrame, path: Path, n: int = 12) -> None:
    df = prices.head(n).iloc[::-1]
    fig, ax = plt.subplots(figsize=(7.5, 5))
    ax.barh(df["Country"], df["mean_price"], color=HIGHLIGHT, height=0.6, label="Mean")
    ax.scatter(df["median_price"], range(len(df)), color=INK, marker="|", s=160,
               zorder=3, label="Median")
    for y, (m, k) in enumerate(zip(df["mean_price"], df["n_reviews"])):
        ax.text(m + 0.8, y, f"${m:.0f}  (n={k:,})", va="center", color=INK_2, fontsize=9)
    ax.set_xlabel("Price per bottle (USD)")
    ax.set_title(f"Highest average bottle price ({n} countries, 100+ reviews each)")
    ax.legend(frameon=False, loc="lower right")
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    _finish(fig, path)


def producer_vs_price_scatter(pvp: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 4.6))
    ax.scatter(pvp["Production_mHL"], pvp["mean_price"], s=70, color=HIGHLIGHT,
               edgecolor=SURFACE, linewidth=2, zorder=3)
    for _, r in pvp.iterrows():
        ax.annotate(r["Country"], (r["Production_mHL"], r["mean_price"]),
                    xytext=(6, 4), textcoords="offset points", color=INK, fontsize=9)
    ax.set_xlabel("Red wine production (million hectolitres)")
    ax.set_ylabel("Mean bottle price (USD)")
    rho = pvp.attrs.get("spearman_rho")
    ax.set_title(f"Bigger producers are only loosely pricier (Spearman ρ = {rho:.2f}, n = {len(pvp)})")
    ax.grid(color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    _finish(fig, path)
