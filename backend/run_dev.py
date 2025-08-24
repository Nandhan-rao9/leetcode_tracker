from src.app import app
from src.config import PORT
from flask_cors import CORS


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=True)

