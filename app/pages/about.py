import dash
from dash import html, dcc

dash.register_page(__name__, path="/about", name="About", order=3)

layout = html.Div(
    [
        html.H3("About"),
        dcc.Markdown(
            """
            This project explores goalkeeper performance across the league and at an individual level.

            **Goals**
            - League-wide distributions and ranking
            - Individual goalkeeper profiles and comparisons
            - Clean, reproducible data sync from S3 to local cache
            """
        ),
    ],
    className="page",
)
