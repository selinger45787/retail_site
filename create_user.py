from app import app, db
from models import User

def create_new_user():
    with app.app_context():
        # Check if user already exists
        username = "Андрій Плахонін"
        user_id = 4578736
        email = f"{user_id}@example.com"  # Creating an email based on the ID
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"Користувач '{username}' вже існує!")
            return
            
        # Create new user
        user = User(username=username, email=email, role="user")
        # Set password same as user ID for simplicity
        user.set_password(str(user_id))
        
        # Add and commit to database
        db.session.add(user)
        db.session.commit()
        
        print(f"Користувач '{username}' успішно створено!")
        print(f"ID: {user_id}")
        print(f"Роль: user")
        print(f"Пароль: {user_id}")

if __name__ == "__main__":
    create_new_user() 