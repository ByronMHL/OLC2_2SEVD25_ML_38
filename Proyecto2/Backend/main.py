from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)

    # Configuración básica
    app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB
	
    # Habilitar CORS para permitir llamadas desde el frontend (Vite)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    return app


if __name__ == "__main__":
	app = create_app()
	app.run(host="0.0.0.0", port=5000, debug=True)