import dash
from dash import html, dcc, Input, Output, callback
import plotly.graph_objects as go

from app.data.store import get_parquet_table
from app.data.transforms import transform_df
from app.components.aggrid import GridSpec, make_aggrid, reset_grid


# -----------------------------
# Page registration & IDs
# -----------------------------
PAGE = "comparative-performance-analysis"

GRID_ID           = f"{PAGE}-grid"
GRID_CONTAINER_ID = f"{PAGE}-grid-container"
RESET_BTN_ID      = f"{PAGE}-reset-filters-btn"
DROPDOWN_ID       = f"{PAGE}-goalkeeper-dropdown"
PLOT_ID           = f"{PAGE}-dynamic-radar-plot"

dash.register_page(__name__, 
                   path="/comparative-performance-analysis", 
                   name="Comparative Performance Analysis", 
                   order=2)


# -----------------------------
# Data loading
# -----------------------------
df = transform_df(get_parquet_table("mart_goalkeeper_league_ratings", None, True))

REFERENCE_COLS = {"Goalkeeper", "Team"}
METRIC_COLS = [col for col in df.columns if col not in REFERENCE_COLS]

# Dropdown options (safe defaults)
gk_values = sorted(df["Goalkeeper"].dropna().unique()) if "Goalkeeper" in df.columns else []
gk_options = [{"label": gk, "value": gk} for gk in gk_values]
default_gk = gk_values[0] if gk_values else None


# -----------------------------
# Grid configuration
# -----------------------------
spec = GridSpec(
    grid_id=GRID_ID,
    reference_cols=("Goalkeeper", "Team"),
    height="50vh",
    dash_grid_options={"rowSelection": "single"},
)
grid = make_aggrid(df, spec)


# -----------------------------
# Layout
# -----------------------------
layout = html.Div(
    [
        html.H3("Standardised Performance & Ranking"),
        html.Div(
            [
                html.Div(id=GRID_CONTAINER_ID, children=grid),
                html.Div(
                    html.Button("Reset filters", id=RESET_BTN_ID, n_clicks=0),
                    className="block-controls",
                ),
            ],
            className="block",
        ),

        html.Div(
            [
                html.H4("Multivariate Performance"),
                dcc.Dropdown(
                    id=DROPDOWN_ID,
                    options=gk_options,
                    value=default_gk,
                    clearable=False,
                    disabled=not bool(gk_options),
                ),
                dcc.Graph(
                    id=PLOT_ID,
                    figure={},
                    style={"height": "60vh"},
                ),
            ],
            className="block",
        ),
    ],
    className="page",
)


# -----------------------------
# Callbacks
# -----------------------------

@callback(
    Output(GRID_CONTAINER_ID, "children"),
    Input(RESET_BTN_ID, "n_clicks"),
    prevent_initial_call=True,
)
def reset_filters(_):
    return reset_grid(df, spec)


@callback(
    Output(PLOT_ID, "figure"),
    Input(DROPDOWN_ID, "value"),
)
def update_graph(goalkeeper):
    pass