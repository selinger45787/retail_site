from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from database import engine, Base
from models import User, Brand, Material, Category, Department, Test, TestQuestion, TestAnswer, TestResult, TestQuestionResult, MaterialImage

def update_database():
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    # Создаем сессию
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Проверяем наличие таблицы users
        if 'users' not in existing_tables:
            print("Creating users table...")
            User.__table__.create(engine)
            
            # Создаем администратора по умолчанию
            from werkzeug.security import generate_password_hash
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
            session.add(admin)
        
        # Проверяем наличие таблицы categories
        if 'category' not in existing_tables:
            print("Creating category table...")
            Category.__table__.create(engine)
            
            # Добавляем базовые категории
            categories = [
                Category(name='Інструкції'),
                Category(name='Презентації'),
                Category(name='Відео'),
                Category(name='Документи')
            ]
            session.add_all(categories)
        
        # Проверяем наличие таблицы brands
        if 'brands' not in existing_tables:
            print("Creating brands table...")
            Brand.__table__.create(engine)
        
        # Проверяем наличие таблицы materials
        if 'materials' not in existing_tables:
            print("Creating materials table...")
            Material.__table__.create(engine)
        
        # Проверяем наличие таблицы material_images
        if 'material_images' not in existing_tables:
            print("Creating material_images table...")
            MaterialImage.__table__.create(engine)
        
        # Проверяем наличие таблицы departments
        if 'departments' not in existing_tables:
            print("Creating departments table...")
            Department.__table__.create(engine)
            
            # Добавляем базовую структуру отделов
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
            session.add_all(departments)
        
        # Проверяем наличие таблиц для тестов
        if 'tests' not in existing_tables:
            print("Creating tests table...")
            Test.__table__.create(engine)
        
        if 'test_question' not in existing_tables:
            print("Creating test_question table...")
            TestQuestion.__table__.create(engine)
        
        if 'test_answer' not in existing_tables:
            print("Creating test_answer table...")
            TestAnswer.__table__.create(engine)
        
        if 'test_result' not in existing_tables:
            print("Creating test_result table...")
            TestResult.__table__.create(engine)
        
        if 'test_question_result' not in existing_tables:
            print("Creating test_question_result table...")
            TestQuestionResult.__table__.create(engine)
        
        session.commit()
        print("Database structure updated successfully!")
        
    except Exception as e:
        session.rollback()
        print(f"Error updating database: {str(e)}")
    finally:
        session.close()

if __name__ == "__main__":
    update_database() 