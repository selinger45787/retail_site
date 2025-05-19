from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from database import Base, engine

def create_tables():
    # Создаем все таблицы
    Base.metadata.create_all(engine)
    
    # Создаем сессию
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Создаем администратора по умолчанию
        from werkzeug.security import generate_password_hash
        from models import User
        
        admin = User(
            username='admin',
            email='admin@abrams.com',
            password_hash=generate_password_hash('admin'),
            first_name='Admin',
            last_name='Admin',
            role='admin',
            department='Офіс',
            position='Адміністратор'
        )
        
        # Создаем базовые категории
        from models import Category
        categories = [
            Category(name='Інструкції'),
            Category(name='Презентації'),
            Category(name='Відео'),
            Category(name='Документи')
        ]
        
        # Создаем базовые отделы
        from models import Department
        departments = [
            Department(name="Компанія", parent_id=None),
            Department(name="Відділ розробки", parent_id=1),
            Department(name="Відділ продажів", parent_id=1),
            Department(name="Відділ маркетингу", parent_id=1),
            Department(name="Frontend команда", parent_id=2),
            Department(name="Backend команда", parent_id=2),
            Department(name="QA команда", parent_id=2),
            Department(name="Регіональні продажі", parent_id=3),
            Department(name="Онлайн продажі", parent_id=3),
            Department(name="SMM", parent_id=4),
            Department(name="Контент", parent_id=4)
        ]
        
        # Добавляем все в базу данных
        session.add(admin)
        session.add_all(categories)
        session.add_all(departments)
        session.commit()
        
        print("All tables created and initial data added successfully!")
        
    except Exception as e:
        session.rollback()
        print(f"Error: {str(e)}")
    finally:
        session.close()

if __name__ == "__main__":
    create_tables() 