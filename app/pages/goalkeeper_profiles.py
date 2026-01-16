import dash
from dash import html

from app.data.store import get_parquet_table  # adjust name if yours differs

dash.register_page(__name__, path="/goalkeeper-profiles", name="Goalkeeper Profiles", order=2)

df = get_parquet_table("mart_goalkeeper_league_ratings", None, True)

layout = html.Div(
    [
        html.H3("Goalkeeper Profiles"),
        html.P(f"Loaded rows: {len(df):,}"),
        html.P("Next: dropdown select GK, profile radar / bar comparisons."),
    ],
    className="page",
)
