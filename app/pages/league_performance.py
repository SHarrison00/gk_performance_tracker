import dash
from dash import html
import dash_ag_grid as dag

from app.data.store import get_parquet_table
from app.data.transforms import transform_df

dash.register_page(__name__, path="/league-performance", name="League Performance", order=1)

df = get_parquet_table("fct_goalkeeper_performance", None, True)
df = transform_df(df)

layout = html.Div(
    [
        html.H3("League Performance"),
        dag.AgGrid(
            rowData=df.to_dict("records"),
            columnDefs=[{"field": i} for i in df.columns],
            )
    ],
    className="page",
)
