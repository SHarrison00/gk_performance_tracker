from pathlib import Path
import dash
from dash import html

from app.components.navbar import Navbar

def create_dash_app(server):
    pages_dir = Path(__file__).resolve().parent / "pages"

    app = dash.Dash(
        __name__,
        server=server,
        use_pages=True,
        pages_folder=str(pages_dir),
        suppress_callback_exceptions=True,
        title="GK Performance Tracker",
    )

    app.layout = html.Div(
        [
            html.Header(
                [
                    html.Div(
                        [
                            html.H2("Goalkeeper Performance Tracker", className="app-title"),
                            html.Div("Developed by Samuel Harrison", className="app-subtitle"),
                        ],
                        className="header-left",
                    ),
                    Navbar(),
                ],
                className="header",
            ),
            html.Main(
                dash.page_container,
                className="main",
            ),
        ],
        className="app-shell",
    )

    return app
