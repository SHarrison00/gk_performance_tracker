import dash
from dash import html

from app.data.store import get_parquet_table

dash.register_page(__name__, path="/league-performance", name="League Performance", order=1)

df = get_parquet_table("fct_goalkeeper_performance", None, True)

layout = html.Div(
    [
        html.H3("League Performance"),
        html.P(f"Loaded rows: {len(df):,}"),
        html.P("Next: distributions, ranks, filters, league comparisons."),
    ],
    className="page",
)
