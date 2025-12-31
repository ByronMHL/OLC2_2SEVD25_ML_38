from flask import Flask
from flask_cors import CORS


def create_app():
	app = Flask(__name__)


	app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB

	CORS(app, resources={r"/api/*": {"origins": "*"}})

	# Blueprints de controllers
	try:
		from controllers.upload import upload_bp
		from controllers.clean import clean_bp
		from controllers.training import training_bp
		from controllers.trainingText import training_text_bp
		from controllers.hyperparameters import hyper_bp 
		from controllers.predict import predict_bp
		from controllers.reports_controller import reports_bp
		from controllers.rendimiento import rendimiento_bp
	except ModuleNotFoundError as e:
		# Solo usar imports relativos si el error es por no encontrar 'controllers'
		if "No module named 'controllers'" in str(e) or "controllers" == getattr(e, "name", ""):
			from .controllers.upload import upload_bp  # type: ignore
			from .controllers.clean import clean_bp  # type: ignore
			from .controllers.training import training_bp  # type: ignore
			from .controllers.trainingText import training_text_bp  # type: ignore
			from .controllers.hyperparameters import hyper_bp  # type: ignore
			from .controllers.predict import predict_bp  # type: ignore
			from .controllers.reports_controller import reports_bp  # type: ignore
			from .controllers.rendimiento import rendimiento_bp  # type: ignore
		else:
			# Re-lanzar errores de dependencias internas (p.ej., 'nltk' ausente)
			raise

	app.register_blueprint(upload_bp, url_prefix="/api")
	app.register_blueprint(clean_bp, url_prefix="/api")
	app.register_blueprint(training_bp, url_prefix="/api")
	app.register_blueprint(training_text_bp, url_prefix="/api")
	app.register_blueprint(hyper_bp, url_prefix="/api")
	app.register_blueprint(predict_bp, url_prefix="/api")
	app.register_blueprint(reports_bp, url_prefix="/api")
	app.register_blueprint(rendimiento_bp, url_prefix="/api")

	return app


if __name__ == "__main__":
	app = create_app()
	app.run(host="0.0.0.0", port=5000, debug=True)
