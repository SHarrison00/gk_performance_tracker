from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

from app import create_app

server = create_app()

if __name__ == "__main__":
    server.run(debug=True, host="127.0.0.1", port=8050)
