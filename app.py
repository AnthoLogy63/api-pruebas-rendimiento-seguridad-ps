from flask import Flask, jsonify

from database.db import init_db
from routes.libro_routes import libros_bp
from routes.prestamo_routes import prestamos_bp
from routes.web_routes import web_bp
from services.exceptions import AppError


def create_app() -> Flask:
    app = Flask(__name__)
    init_db()
    app.register_blueprint(web_bp)
    app.register_blueprint(libros_bp)
    app.register_blueprint(prestamos_bp)

    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        return jsonify({"success": False, "error": error.message}), error.status_code

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({"success": False, "error": "Ruta no encontrada"}), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return jsonify({"success": False, "error": "Método HTTP no permitido"}), 405

    @app.errorhandler(500)
    def handle_internal_error(error):
        return jsonify({"success": False, "error": "Error interno del servidor"}), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
