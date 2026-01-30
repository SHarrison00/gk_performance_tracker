import numpy as np
import pandas as pd
import plotly.graph_objects as go

REFERENCE_COLS = ["Goalkeeper", "Team"]

# Set key metrics for analysis
METRIC_CONFIG = {
    "Save %": "{:.1f}%",
    "PSxG − GA": "{:.1f}",
    "Crosses Stopped %": "{:.1f}%",
    "Pass Attempts (per 90)": "",
    "Long Kick Pass Completion %": "{:.1f}%",
    "Def Actions OPA (per 90)": "{:.1f}",
}

METRIC_COLS = list(METRIC_CONFIG)
METRIC_FMTS = {c: METRIC_CONFIG[c] for c in METRIC_COLS}
 

def format_metric(value, fmt: str):
    """Format metric value using foramt; return raw value if fmt is empty."""
    return fmt.format(value) if fmt else value


def get_goalkeeper_data_radar_plot(
    goalkeeper: str, df: pd.DataFrame
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Get goalkeeper data in neccessary format for radar plot."""
    gk_row = df.loc[df["Goalkeeper"] == goalkeeper].squeeze()

    raw_values = pd.Series({col: format_metric(gk_row.at[col], METRIC_CONFIG[col]) for col in METRIC_COLS})

    z_scores = gk_row[[f"Z: {col}" for col in METRIC_COLS]].rename(
        {f"Z: {col}": col for col in METRIC_COLS}
    )
    percentiles = gk_row[[f"Pctile: {col}" for col in METRIC_COLS]].rename(
        {f"Pctile: {col}": col for col in METRIC_COLS}
    )

    return raw_values, z_scores, percentiles


def get_radar_chart(goalkeepers: str | list[str], df: pd.DataFrame) -> go.Figure:
    """Create a radar chart comparing one or more goalkeepers across key performance metrics."""
    fig = go.Figure()

    if not goalkeepers:
        fig.update_layout(title="Goalkeeper Performance")
        return fig
    if isinstance(goalkeepers, str):
        goalkeepers = [goalkeepers]

    max_abs = 0.0

    for gk in goalkeepers:
        raw_values, z_scores, percentiles = get_goalkeeper_data_radar_plot(gk, df)

        z = z_scores.reindex(METRIC_COLS).to_numpy()
        max_abs = max(max_abs, float(np.nanmax(np.abs(z))))

        customdata = np.column_stack([
            raw_values.reindex(METRIC_COLS).to_numpy(),
            percentiles.reindex(METRIC_COLS).to_numpy(),
        ])

        fig.add_trace(
            go.Scatterpolar(
                r = z,
                theta = METRIC_COLS,
                fill = "toself",
                name = gk.replace("_", " ").title(),
                customdata = customdata,
                hovertemplate = (
                    "<b>%{METRIC_COLS}</b><br>"
                    "Value: %{customdata[0]}<br>"
                    "Percentile: %{customdata[1]:.0f}th<br>"
                    "Z-score: %{r:.2f}<br>"
                    "<extra></extra>"
                ),
            )
        )
    
    if max_abs == 0 or np.isnan(max_abs):
        max_abs = 1

    fig.update_layout(
        polar = dict(radialaxis = dict(visible = True, range=[-max_abs, max_abs])),
        showlegend = True,
        title = "Goalkeeper Performance",
    )
    return fig
