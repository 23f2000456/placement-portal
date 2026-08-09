import os
from celery import Celery
from celery.schedules import crontab
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_caching import Cache
from flask_cors import CORS

db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()
celery = Celery(__name__)
cache = Cache()


def create_app(config_class="backend.config.Config"):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)
    CORS(app, origins=["http://localhost:8080", "http://localhost:8081"])

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    cache.init_app(app)

    celery.conf.update(
        broker_url=app.config['CELERY_BROKER_URL'],
        result_backend=app.config['CELERY_RESULT_BACKEND'],
        beat_schedule={
            'daily-interview-reminders': {
                'task': 'backend.tasks.reminders.send_interview_reminders',
                'schedule': crontab(hour=8, minute=0),
            },
            'monthly-placement-report': {
                'task': 'backend.tasks.reports.send_monthly_report',
                'schedule': crontab(hour=9, minute=0, day_of_month=1),
            },
        }
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    from backend import models  

    from backend.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from backend.routes.admin import admin_bp
    app.register_blueprint(admin_bp)

    from backend.routes.company import company_bp
    app.register_blueprint(company_bp)

    from backend.routes.student import student_bp
    app.register_blueprint(student_bp)

    return app