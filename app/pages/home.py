import dash
from dash import html, dcc

dash.register_page(__name__, path="/", name="Home", order=0)

layout = html.Div(
    [
        html.H3("Goalkeeper Performance Tracker"),
        dcc.Markdown(
            """
            A lightweight analytics platform for comparing Premier League goalkeeper
            performance — built as a personal data engineering project.

            Goalkeeper performance is assessed across four dimensions:

            | Dimension | Description |
            |-----------|-------------|
            | **Shot Stopping** | Save % and PSxG − GA (goals prevented relative to shot quality) |
            | **Crossing** | Percentage of opposition crosses successfully claimed or cleared |
            | **Distribution** | Pass attempts per 90 and long kick completion rate |
            | **Sweeping** | Defensive actions outside the penalty area per 90 |

            Metrics are standardised at the league level using z-scores and percentile ranks,
            enabling fair comparison across goalkeepers regardless of playing style or team context.

            **Data source:** Match-level data is scraped from [FBRef.com](https://fbref.com/en/)
            and processed through a dbt pipeline backed by DuckDB.

            ---

            Head to the **Performance Overview** tab to explore raw statistics across the league,
            or the **Comparative Performance Analysis** tab to compare goalkeepers side by side
            using a standardised radar chart.
            """
        ),
    ],
    className="page",
)
