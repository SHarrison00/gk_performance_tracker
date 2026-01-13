# Import packages
from dash import Dash, html, dcc, callback, Output, Input
import dash_ag_grid as dag
import pandas as pd
import plotly.express as px

# TO DO: Update to request data from S3
df = pd.read_parquet('/Users/samharrison/Documents/data_sci/gk_performance_tracker/gk_performance_tracker/public/fct_goalkeeper_performance.parquet')


# Initialize the app
app = Dash()

app.layout = [
    html.Div(children='My First App with Data, Graph, and Controls'),
    html.Hr(),
    dcc.RadioItems(options=['saves', 'clean_sheets', 'save_pct'], value='saves', id='controls-and-radio-item'),
    dag.AgGrid(
        rowData=df.to_dict('records'),
        columnDefs=[{"field": i} for i in df.columns]
    ),
    dcc.Graph(figure={}, id='controls-and-graph')
]

# Add controls to build the interaction
@callback(
    Output(component_id='controls-and-graph', component_property='figure'),
    Input(component_id='controls-and-radio-item', component_property='value')
)
def update_graph(col_chosen):
    fig = px.histogram(df, x='goalkeeper', y=col_chosen, histfunc='max')
    return fig


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
