from backend import create_app, db
from backend.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    db.create_all()

    admin_email = app.config["ADMIN_EMAIL"]
    existing_admin = User.query.filter_by(email=admin_email, role="admin").first()

    if not existing_admin:
        admin = User(
            email=admin_email,
            password=generate_password_hash(app.config["ADMIN_PASSWORD"]),
            role="admin"
        )
        db.session.add(admin)
        db.session.commit()

    print("Database setup complete.")