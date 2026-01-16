from app.server import create_server
from app.dash_app import create_dash_app
from app.data.sync import sync_data

def create_app():
    server = create_server()
    
    sync_data(server.config)
    
    create_dash_app(server)  # attaches dash to Flask
    return server
