import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
jwt = JWTManager()


def create_app(config_class="backend.config.Config"):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    jwt.init_app(app)

    from backend import models  # registers models with SQLAlchemy

    from backend.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from backend.routes.admin import admin_bp
    app.register_blueprint(admin_bp)

    return app