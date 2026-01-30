import dash
from dash import html, dcc, Input, Output, callback

from app.data.store import get_parquet_table
from app.data.transforms import transform_df, get_valid_goalkeepers, get_n_highest_ranked_goalkeepers
from app.components.aggrid import GridSpec, make_aggrid, reset_grid
from app.components.radar import get_radar_chart

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

REFERENCE_COLS = ["Goalkeeper", "Team"]


# -----------------------------
# Grid configuration
# -----------------------------
spec = GridSpec(
    grid_id=GRID_ID,
    reference_cols=REFERENCE_COLS,
    height="50vh",
    dash_grid_options={"rowSelection": "single"},
)
grid = make_aggrid(df, spec)


# -----------------------------
# Radar chart configuration
# -----------------------------
gk_values = get_valid_goalkeepers(df)
gk_options = [{"label": gk, "value": gk} for gk in gk_values]
valid_gks = set(gk_values)

default_gks = get_n_highest_ranked_goalkeepers(df, n=3)
initial_fig = get_radar_chart(default_gks, df)

MAX_GKS = 5


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
                    value=default_gks,
                    multi=True,
                    clearable=False,
                    disabled=not bool(gk_options),
                ),
                dcc.Graph(
                    id=PLOT_ID, # Placeholder for Radar chart
                    figure=initial_fig,
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
    Output(DROPDOWN_ID, "value"),
    Input(DROPDOWN_ID, "value"),
    prevent_initial_call=True,
)
def limit_goalkeeper_selection(selected):
    if not selected:
        return selected
    if len(selected) <= MAX_GKS:
        return selected
    # Keep the first selected GKs
    return selected[:MAX_GKS]


@callback(
    Output(PLOT_ID, "figure"),
    Input(DROPDOWN_ID, "value"),
)
def update_graph(goalkeepers):
    if not goalkeepers:
        return get_radar_chart([], df)

    if isinstance(goalkeepers, str):
        goalkeepers = [goalkeepers]

    goalkeepers = [g for g in goalkeepers if g in valid_gks]
    
    return get_radar_chart(goalkeepers, df)
