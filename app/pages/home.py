import dash
from dash import html

dash.register_page(__name__, path="/", name="Home", order=0)

layout = html.Div(
    [
        html.H3("Home"),
        html.P("Welcome. This will become the landing page for the project."),
    ],
    className="page",
)
