from app import app, db
from models import User

def create_admin():
    with app.app_context():
        # Проверим, существует ли уже администратор
        existing_admin = User.query.filter_by(username='admin').first()
        if existing_admin:
            print('Администратор уже существует!')
            return
        
        # Создаем нового администратора
        admin = User(
            username='admin',
            role='admin',
            department='other',
            position='other_position'
        )
        admin.set_password('HerokuDBUdmYlo12345')
        db.session.add(admin)
        db.session.commit()
        print('Администратор успешно создан!')
        print(f'Логин: admin')
        print(f'Пароль: HerokuDBUdmYlo12345')

if __name__ == '__main__':
    create_admin() 