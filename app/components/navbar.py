from dash import html, dcc
import dash

def Navbar():
    # Dash pages registry is populated after pages are imported.
    pages = list(dash.page_registry.values())

    # Sort by 'order' if present, otherwise by name
    pages.sort(key=lambda p: p.get("order", 999))

    return html.Nav(
        [
            dcc.Link(
                page["name"],
                href=page["relative_path"],
                className="nav-link",
            )
            for page in pages
        ],
        className="navbar",
    )
