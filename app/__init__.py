import os
from flask import Flask, redirect, url_for
from flask import Flask
from app.routes.bulk_prediction import bulk_prediction
from app.config import Config
from app.extensions import db, login_manager


def create_app(config_class=Config):

    app = Flask(__name__)

    app.config.from_object(config_class)

    # Make sure instance directory exists
    os.makedirs(
        os.path.join(
            app.root_path,
            "..",
            "instance"
        ),
        exist_ok=True
    )

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Import models so SQLAlchemy knows them
    from app.models import (
        User,
        Employee,
        Prediction,
        RiskIndicator
    )

    # Register blueprints
    from app.routes.auth import auth
    from app.routes.dashboard import dashboard
    from app.routes.employee import employee
    from app.routes.prediction import prediction
    from app.routes.reports import reports
    from app.routes.bulk_prediction import bulk_prediction


    app.register_blueprint(auth)
    app.register_blueprint(dashboard)
    app.register_blueprint(employee)
    app.register_blueprint(prediction)
    app.register_blueprint(reports)
    app.register_blueprint(bulk_prediction)

    # Create database tables
    with app.app_context():
        db.create_all()
    @app.route("/")
    def index():

        return redirect(
        url_for("auth.login")
    )    

    return app


@login_manager.user_loader
def load_user(user_id):

    from app.models import User

    return User.query.get(int(user_id))