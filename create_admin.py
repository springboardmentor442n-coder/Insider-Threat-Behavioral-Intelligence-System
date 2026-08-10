from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import User


app = create_app()


with app.app_context():

    existing_user = User.query.filter_by(
        username="admin"
    ).first()

    if existing_user:

        print("Admin user already exists.")

    else:

        user = User(
            username="admin",
            email="admin@insiderthreat.local",
            password_hash=generate_password_hash("admin123"),
            role="analyst"
        )

        db.session.add(user)
        db.session.commit()

        print("Admin user created successfully.")
        print("Username: admin")
        print("Password: admin123")