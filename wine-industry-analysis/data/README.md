# Data

| File | Source | In repo? |
|---|---|---|
| `raw/OIV_Wine_Data.xlsx` | International Organisation of Vine and Wine (OIV) production figures, compiled into four sheets | Yes |
| `raw/winemag-data_first150k.csv` | Wine Enthusiast reviews scraped in 2017, published on Kaggle as [Wine Reviews](https://www.kaggle.com/datasets/zynicide/wine-reviews) | No, 50 MB |

To run the analysis, download `winemag-data_first150k.csv` from the Kaggle page and put it in `data/raw/`.

## OIV workbook sheets

| Sheet | Columns | Unit |
|---|---|---|
| `Red_Wine_By_Country` | Country, Production_mHL | million hectolitres |
| `Global_Red_By_Country` | Country, Period, Share | % of world red production |
| `USA_Production_By_Colour` | Year, Red, White, Rosé | million hectolitres, 2000 to 2021 |
| `Consumption_By_Color` | Wine_Color, Percentage | % of world consumption |

## Cleaning the reviews

The 150k file has many exact duplicate rows, because the same review was scraped more than once. The loader drops them before any averaging. Rows with no price or no country are also dropped. `outputs/summary.json` records the counts from each step.
