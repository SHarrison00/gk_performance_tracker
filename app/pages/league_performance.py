import dash
from dash import html, dcc, Input, Output, callback
import dash_ag_grid as dag

from app.data.store import get_parquet_table
from app.data.transforms import transform_df

dash.register_page(__name__, path="/league-performance", name="League Performance", order=1)

# Load raw data from local parquet cache, then apply presentation transforms
df = transform_df(get_parquet_table("fct_goalkeeper_performance", None, True))

PINNED_COLS = {"Goalkeeper", "Team"}

column_defs = [
    {
        "field": col,
        **({"pinned": "left"} if col in PINNED_COLS else {}),
    }
    for col in df.columns
]

DEFAULT_COL_DEF = {"sortable": True, "filter": True, "resizable": True}


def make_league_grid():
    return dag.AgGrid(
        id="league-grid",
        rowData=df.to_dict("records"),
        columnDefs=column_defs,
        defaultColDef=DEFAULT_COL_DEF,
        style={"height": "75vh"},
    )


layout = html.Div(
    [
        html.H3("League Performance"),

        # Block 1: Grid
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

        # Block 2: Visuals (placeholder for now)
        html.Div(
            [
                html.H4("Visuals"),
                dcc.Graph(
                    id="league-plot-1",
                    figure={},  # placeholder
                    style={"height": "40vh"},
                ),
            ],
            className="block",
        ),
    ],
    className="page",
)


@callback(
    Output("grid-container", "children"),
    Input("reset-filters-btn", "n_clicks"),
    prevent_initial_call=True,
)
def reset_filters(_):
    # Remount the grid to clear filters/sorts/column state
    return make_league_grid()
