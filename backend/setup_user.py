from config import app, db
from models import User

with app.app_context():
    # Create or update demo user
    user = User.query.filter_by(username="demo_user").first()
    if user:
        print("Updating password for demo_user")
        user.set_password("password")
    else:
        print("Creating demo_user")
        user = User(username="demo_user")
        user.set_password("password")
        db.session.add(user)
    db.session.commit()
    print("Demo user setup complete: username=demo_user, password=password")

