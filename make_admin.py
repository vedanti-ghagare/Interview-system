from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    user = User.query.filter_by(username="vedanti").first()

    if user:
        user.role = "admin"
        db.session.commit()
        print("User is now an admin.")
    else:
        print("User not found.")