"""The three questions from the investor case, answered as tables.

1. Where is wine made?                 -> top_producers, share_shift
2. How is U.S. production changing?    -> usa_colour_trend
3. Which countries charge the most?    -> price_by_country, producer_vs_price
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# A country needs at least this many priced reviews before its average price is
# reported. Below it, one or two luxury bottles can decide the ranking.
MIN_REVIEWS = 100


def top_producers(oiv: dict[str, pd.DataFrame], n: int = 5) -> pd.DataFrame:
    """Largest red-wine producers (million hectolitres), with share of the top 10."""
    df = oiv["Red_Wine_By_Country"].sort_values("Production_mHL", ascending=False)
    df = df.assign(Share_of_top10_pct=100 * df["Production_mHL"] / df["Production_mHL"].sum())
    return df.head(n).reset_index(drop=True)


def share_shift(oiv: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Change in each country's share of world red production, first vs last period."""
    wide = oiv["Global_Red_By_Country"].pivot(index="Country", columns="Period", values="Share")
    first, last = wide.columns.min(), wide.columns.max()
    wide["Change_pts"] = wide[last] - wide[first]
    return wide.sort_values("Change_pts").reset_index()


def usa_colour_trend(usa_long: pd.DataFrame) -> pd.DataFrame:
    """Start, end, total change and compound annual growth for each colour."""
    rows = []
    for colour, g in usa_long.groupby("Colour", sort=False):
        g = g.sort_values("Year")
        start_year, end_year = int(g["Year"].iloc[0]), int(g["Year"].iloc[-1])
        start, end = g["Production_mHL"].iloc[0], g["Production_mHL"].iloc[-1]

        # CAGR is undefined from a zero start (rosé is 0 in the early years),
        # so measure rosé from its first non-zero year instead.
        nonzero = g[g["Production_mHL"] > 0]
        base_year, base = int(nonzero["Year"].iloc[0]), nonzero["Production_mHL"].iloc[0]
        years = end_year - base_year
        cagr = (end / base) ** (1 / years) - 1 if years > 0 else np.nan

        rows.append(
            {
                "Colour": colour,
                f"mHL_{start_year}": start,
                f"mHL_{end_year}": end,
                "Change_mHL": end - start,
                "CAGR_from_year": base_year,
                "CAGR_pct": 100 * cagr,
            }
        )
    out = pd.DataFrame(rows)

    totals = usa_long.groupby("Year")["Production_mHL"].sum()
    white = usa_long[usa_long["Colour"] == "White"].set_index("Year")["Production_mHL"]
    out.attrs["white_share_pct"] = (100 * white / totals).round(1).to_dict()
    return out


def price_by_country(reviews: pd.DataFrame, min_reviews: int = MIN_REVIEWS) -> pd.DataFrame:
    """Mean and median bottle price by country, with a 95% CI on the mean.

    Wine prices are heavily right-skewed, so the median is reported next to the
    mean: a country with a few very expensive bottles can have a high mean and
    an ordinary median.
    """
    g = reviews.groupby("country")["price"]
    out = pd.DataFrame(
        {
            "n_reviews": g.size(),
            "mean_price": g.mean(),
            "median_price": g.median(),
            "sem": g.sem(),
        }
    )
    out = out[out["n_reviews"] >= min_reviews].copy()
    out["ci95_low"] = out["mean_price"] - 1.96 * out["sem"]
    out["ci95_high"] = out["mean_price"] + 1.96 * out["sem"]
    out = out.drop(columns="sem").sort_values("mean_price", ascending=False)
    return out.reset_index().rename(columns={"country": "Country"})


def producer_vs_price(oiv: dict[str, pd.DataFrame], prices: pd.DataFrame) -> pd.DataFrame:
    """Join production rank with price rank for the countries in both sources.

    This is the investor's key comparison: if volume and price ranks agreed,
    the biggest producers would also be the priciest. Spearman's rho measures
    how far they agree.
    """
    prod = oiv["Red_Wine_By_Country"][["Country", "Production_mHL"]]
    merged = prod.merge(prices[["Country", "mean_price", "median_price", "n_reviews"]], on="Country")
    merged["production_rank"] = merged["Production_mHL"].rank(ascending=False).astype(int)
    merged["price_rank"] = merged["mean_price"].rank(ascending=False).astype(int)
    merged = merged.sort_values("production_rank").reset_index(drop=True)
    merged.attrs["spearman_rho"] = merged["Production_mHL"].corr(merged["mean_price"], method="spearman")
    return merged
