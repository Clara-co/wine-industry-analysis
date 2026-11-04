"""Run the full analysis:  python -m wine_analysis

Writes CSV tables to outputs/tables, PNG charts to outputs/figures, and a
machine-readable summary to outputs/summary.json.
"""

from __future__ import annotations

import json
from pathlib import Path

from . import analysis, charts, load

OUT = Path(__file__).resolve().parents[2] / "outputs"


def main() -> None:
    (OUT / "tables").mkdir(parents=True, exist_ok=True)
    (OUT / "figures").mkdir(parents=True, exist_ok=True)

    oiv = load.load_oiv()
    usa_long = load.usa_production_long(oiv)
    reviews = load.load_reviews()

    top = analysis.top_producers(oiv)
    shift = analysis.share_shift(oiv)
    trend = analysis.usa_colour_trend(usa_long)
    prices = analysis.price_by_country(reviews)
    pvp = analysis.producer_vs_price(oiv, prices)

    top.round(2).to_csv(OUT / "tables" / "top_producers.csv", index=False)
    shift.round(2).to_csv(OUT / "tables" / "red_share_shift.csv", index=False)
    trend.round(2).to_csv(OUT / "tables" / "usa_colour_trend.csv", index=False)
    prices.round(2).to_csv(OUT / "tables" / "price_by_country.csv", index=False)
    pvp.round(2).to_csv(OUT / "tables" / "producer_vs_price.csv", index=False)

    charts.top_producers_bar(top, OUT / "figures" / "top_producers.png")
    charts.usa_colour_lines(usa_long, OUT / "figures" / "usa_production_by_colour.png")
    charts.price_bar(prices, OUT / "figures" / "price_by_country.png")
    charts.producer_vs_price_scatter(pvp, OUT / "figures" / "producer_vs_price.png")

    white_share = trend.attrs["white_share_pct"]
    summary = {
        "cleaning": reviews.attrs["cleaning_log"],
        "top_producers": top["Country"].tolist(),
        "priciest_countries_by_mean": prices.head(5)["Country"].tolist(),
        "spearman_production_vs_price": round(pvp.attrs["spearman_rho"], 3),
        "usa_white_share_first_last": {
            str(min(white_share)): white_share[min(white_share)],
            str(max(white_share)): white_share[max(white_share)],
        },
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
