"""Flask application factory."""

from __future__ import annotations

import logging

from flask import Flask, jsonify, render_template

from config import Config
from app.extensions import db


def create_app(config_object=Config) -> Flask:
    Config.ensure_dirs()

    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(config_object)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s | %(message)s",
    )

    if app.config.get("JWT_SECRET") == Config.DEV_SECRET and not app.config.get("TESTING"):
        app.logger.warning(
            "Running with the published development secret. Set SECRET_KEY and "
            "JWT_SECRET in .env before exposing this service."
        )

    db.init_app(app)
    with app.app_context():
        from app.models import seed_analysts  # noqa: PLC0415

        db.create_all()
        created = seed_analysts(app.config["SEED_ANALYSTS"])
        if created:
            app.logger.info("Seeded analyst accounts: %s", ", ".join(created))

    _register_blueprints(app)
    _register_errors(app)
    _init_engine(app)

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/health")
    def health():
        from app.ml import engine as eng  # noqa: PLC0415

        status = eng.engine_status()
        return jsonify({"status": "ok" if status["ready"] else "degraded",
                        "engine": status}), (200 if status["ready"] else 503)

    return app


def _register_blueprints(app: Flask):
    from app.api.auth_routes import bp as auth_bp  # noqa: PLC0415
    from app.api.export_routes import bp as export_bp  # noqa: PLC0415
    from app.api.intel_routes import bp as intel_bp  # noqa: PLC0415
    from app.api.monitor_routes import bp as monitor_bp  # noqa: PLC0415

    for bp in (auth_bp, intel_bp, monitor_bp, export_bp):
        app.register_blueprint(bp)


def _register_errors(app: Flask):
    @app.errorhandler(400)
    def bad_request(err):
        return jsonify({"error": "bad request", "detail": str(err)}), 400

    @app.errorhandler(404)
    def not_found(err):
        return jsonify({"error": "not found"}), 404

    @app.errorhandler(500)
    def server_error(err):
        app.logger.exception("Unhandled error")
        return jsonify({"error": "internal server error"}), 500


def _init_engine(app: Flask):
    """Load ML artefacts at boot; stay up (degraded) if they are missing."""
    from app.ml import engine as eng  # noqa: PLC0415

    engine = eng.init_engine(
        app.config.get("MODEL_DIR"), app.config.get("FEATURES_CSV")
    )
    if engine is None:
        app.logger.warning(
            "Threat engine not loaded — %s", eng.engine_status()["error"]
        )
    else:
        app.logger.info(
            "Threat engine ready: %s over %s user-days",
            engine.metrics.get("model", "model"), f"{len(engine.df):,}",
        )
