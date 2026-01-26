import dash
from dash import html, dcc, Input, Output, callback
import plotly.express as px

from app.data.store import get_parquet_table
from app.data.transforms import transform_df
from app.components.aggrid import GridSpec, make_aggrid, reset_grid


# -----------------------------
# Page registration & IDs
# -----------------------------
PAGE = "performance-overview"

GRID_ID            = f"{PAGE}-grid"
GRID_CONTAINER_ID  = f"{PAGE}-grid-container"
RESET_BTN_ID       = f"{PAGE}-reset-filters-btn"
METRIC_DROPDOWN_ID = f"{PAGE}-metric-dropdown"
PLOT_ID            = f"{PAGE}-dynamic-bar-plot"

dash.register_page(__name__, 
                   path="/performance-overview", 
                   name="Performance Overview", 
                   order=1)


# -----------------------------
# Data loading
# -----------------------------
df = transform_df(get_parquet_table("fct_goalkeeper_performance", None, True))

REFERENCE_COLS = {"Goalkeeper", "Team"}
METRIC_COLS = [col for col in df.columns if col not in REFERENCE_COLS]


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
        html.H3("All Performance Metrics"),

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
                html.H4("Metric Explorer"),
                dcc.Dropdown(
                    id=METRIC_DROPDOWN_ID,
                    options=[{"label": m, "value": m} for m in METRIC_COLS],
                    value=METRIC_COLS[0] if METRIC_COLS else None,
                    clearable=False,
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

# Reset grid by remounting AG Grid (clears filters & sorting)
@callback(
    Output(GRID_CONTAINER_ID, "children"),
    Input(RESET_BTN_ID, "n_clicks"),
    prevent_initial_call=True,
)
def reset_filters(_):
    return reset_grid(df, spec)


# Update bar chart when metric changes
@callback(
    Output(PLOT_ID, "figure"),
    Input(METRIC_DROPDOWN_ID, "value"),
)
def update_graph(metric):
    dff = df.sort_values(metric, ascending=False)
    return px.bar(
        dff,
        x="Goalkeeper",
        y=metric,
        title=f"{metric} by Goalkeeper",
    )
