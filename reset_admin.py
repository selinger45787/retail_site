from app import app, db
from models import User

def reset_admin_password():
    with app.app_context():
        # Find or create admin user
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='admin@example.com', role='admin')
            db.session.add(admin)
        
        # Set new password
        admin.set_password('admin')
        db.session.commit()
        print("Admin password has been reset successfully!")

if __name__ == '__main__':
    reset_admin_password() 