"""Load and clean the two raw data sources.

* OIV workbook: production volumes and shares by country and by wine colour.
* Wine Enthusiast reviews (``winemag-data_first150k.csv``): one row per review,
  with the bottle price and the country of origin.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
OIV_PATH = RAW_DIR / "OIV_Wine_Data.xlsx"
REVIEWS_PATH = RAW_DIR / "winemag-data_first150k.csv"

# The reviews file says "US"; the OIV file says "USA". Use one name everywhere.
COUNTRY_ALIASES = {"US": "USA", "United States": "USA"}


def load_oiv(path: Path = OIV_PATH) -> dict[str, pd.DataFrame]:
    """Return every sheet of the OIV workbook, with tidy column names."""
    sheets = pd.read_excel(path, sheet_name=None)
    for df in sheets.values():
        df.columns = [str(c).strip() for c in df.columns]
        if "Country" in df.columns:
            df["Country"] = df["Country"].str.strip().replace(COUNTRY_ALIASES)
    return sheets


def usa_production_long(oiv: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """U.S. production by colour, reshaped to one row per (year, colour)."""
    wide = oiv["USA_Production_By_Colour"]
    return wide.melt(id_vars="Year", var_name="Colour", value_name="Production_mHL")


def load_reviews(path: Path = REVIEWS_PATH) -> pd.DataFrame:
    """Load the reviews and remove the problems that would bias average prices.

    The 150k file is known to contain many exact duplicate rows (the same review
    scraped more than once). Duplicates would over-count whichever countries
    were scraped repeatedly, so they are dropped before any averaging.
    """
    df = pd.read_csv(path, index_col=0)
    n_raw = len(df)

    df = df.drop_duplicates()
    n_dedup = len(df)

    df = df.dropna(subset=["country", "price"])
    df["country"] = df["country"].str.strip().replace(COUNTRY_ALIASES)

    df.attrs["cleaning_log"] = {
        "raw_rows": n_raw,
        "duplicates_removed": n_raw - n_dedup,
        "rows_missing_price_or_country": n_dedup - len(df),
        "rows_used": len(df),
    }
    return df
