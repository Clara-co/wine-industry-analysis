import pandas as pd
import pytest

from wine_analysis import analysis, load


@pytest.fixture
def oiv():
    return {
        "Red_Wine_By_Country": pd.DataFrame(
            {"Country": ["Italy", "Spain", "USA"], "Production_mHL": [20.0, 14.0, 7.0]}
        ),
        "Global_Red_By_Country": pd.DataFrame(
            {
                "Country": ["Italy", "Italy", "Spain", "Spain"],
                "Period": ["2000-2006", "2014-2021"] * 2,
                "Share": [18.9, 17.3, 11.5, 13.5],
            }
        ),
        "USA_Production_By_Colour": pd.DataFrame(
            {"Year": [2000, 2001, 2002], "Red": [5.0, 5.0, 5.0],
             "White": [10.0, 11.0, 12.1], "Rosé": [0.0, 1.0, 1.21]}
        ),
    }


def test_load_reviews_drops_duplicates_and_missing(tmp_path):
    csv = tmp_path / "r.csv"
    pd.DataFrame(
        {"country": ["US", "US", "France", None], "price": [10, 10, None, 5],
         "points": [90, 90, 88, 85]}
    ).to_csv(csv)
    # index_col=0 makes the duplicate rows identical apart from the index
    df = load.load_reviews(csv)
    log = df.attrs["cleaning_log"]
    assert log["duplicates_removed"] == 1
    assert log["rows_used"] == 1
    assert df["country"].tolist() == ["USA"]  # alias applied


def test_price_by_country_respects_minimum():
    reviews = pd.DataFrame({"country": ["A"] * 3 + ["B"] * 1, "price": [10, 20, 30, 999]})
    out = analysis.price_by_country(reviews, min_reviews=2)
    assert out["Country"].tolist() == ["A"]
    assert out.loc[0, "mean_price"] == 20
    assert out.loc[0, "median_price"] == 20


def test_usa_trend_cagr_starts_at_first_nonzero_year(oiv):
    trend = analysis.usa_colour_trend(load.usa_production_long(oiv)).set_index("Colour")
    assert trend.loc["White", "CAGR_pct"] == pytest.approx(10.0, abs=0.01)
    assert trend.loc["Rosé", "CAGR_from_year"] == 2001
    assert trend.loc["Rosé", "CAGR_pct"] == pytest.approx(21.0, abs=0.01)
    assert trend.loc["Red", "CAGR_pct"] == pytest.approx(0.0)


def test_share_shift_sign(oiv):
    shift = analysis.share_shift(oiv).set_index("Country")
    assert shift.loc["Italy", "Change_pts"] == pytest.approx(-1.6)
    assert shift.loc["Spain", "Change_pts"] == pytest.approx(2.0)


def test_producer_vs_price_ranks(oiv):
    prices = pd.DataFrame(
        {"Country": ["Italy", "Spain", "USA"], "mean_price": [30.0, 20.0, 40.0],
         "median_price": [25.0, 18.0, 30.0], "n_reviews": [100, 100, 100]}
    )
    pvp = analysis.producer_vs_price(oiv, prices).set_index("Country")
    assert pvp.loc["Italy", "production_rank"] == 1
    assert pvp.loc["USA", "price_rank"] == 1
