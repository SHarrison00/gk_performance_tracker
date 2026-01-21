import dash
from dash import html, dcc, Input, Output, callback
import dash_ag_grid as dag
import plotly.express as px

from app.data.store import get_parquet_table
from app.data.transforms import transform_df

dash.register_page(__name__, path="/league-performance", name="League Performance", order=1)

# Load raw data from local parquet cache, then apply presentation transforms
df = transform_df(get_parquet_table("fct_goalkeeper_performance", None, True))

REFERENCE_COLS = {"Goalkeeper", "Team"}
METRIC_COLS = [col for col in df.columns if col not in REFERENCE_COLS]
DEFAULT_COL_DEF = {"sortable": True, "filter": True, "resizable": True}

column_defs = [
    {
        "field": col,
        **({"pinned": "left"} if col in REFERENCE_COLS else {}),
    }
    for col in df.columns
]


# Create dash AG grid object
def make_league_grid():
    return dag.AgGrid(
        id="league-grid",
        rowData=df.to_dict("records"),
        columnDefs=column_defs,
        defaultColDef=DEFAULT_COL_DEF,
        style={"height": "50vh"},
    )

# Set page layout
layout = html.Div(
    [
        html.H3("League Performance"),
        html.Div(
            [
                html.Div(id="grid-container", children=make_league_grid()),
                html.Div(
                    html.Button("Reset filters", id="reset-filters-btn", n_clicks=0),
                    className="block-controls",
                ),
            ],
            className="block",
        ),

        html.Div(
            [
                html.H4("Metric Explorer"),
                dcc.Dropdown(
                    id="metric-dropdown",
                    options=[{"label": m, "value": m} for m in METRIC_COLS],
                    value="Matches Played",
                    clearable=False,
                ),           
                dcc.Graph(
                    id="dynamic-bar-plot",
                    figure={},
                    style={"height": "60vh"},
                ),
            ],
            className="block",
        ),
    ],
    className="page",
)

# League grid component
@callback(
    Output(component_id="grid-container", component_property="children"),
    Input(component_id="reset-filters-btn", component_property="n_clicks"),
    prevent_initial_call=True,
)
def reset_filters(_):
    """Remound the grid to clear filters / sorts."""
    return make_league_grid()

# Dynamic bar plot component
@callback(
    Output("dynamic-bar-plot", "figure"),
    Input("metric-dropdown", "value"),
)
def update_graph(col_chosen):
    dff = df.sort_values(col_chosen, ascending=False)
    fig = px.bar(dff, x="Goalkeeper", y=col_chosen, title=f"{col_chosen} by Goalkeeper")
    return fig
