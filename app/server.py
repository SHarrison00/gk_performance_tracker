from flask import Flask
from app.config import Config

def create_server() -> Flask:
    server = Flask(__name__)
    server.config.from_object(Config)

    @server.get("/health")
    def health():
        return {"status": "ok"}

    return server
