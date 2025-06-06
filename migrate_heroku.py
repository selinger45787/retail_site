#!/usr/bin/env python3
"""
Скрипт для применения миграций на Heroku
"""
import os
from flask import Flask
from flask_migrate import upgrade
from models import db
from sqlalchemy import text

app = Flask(__name__)

# Настройка для Heroku
environment = os.getenv('FLASK_ENV', 'production')
if environment == 'production':
    from config_production import ProductionConfig
    app.config.from_object(ProductionConfig)
else:
    from config import config
    app.config.from_object(config['development'])

# Исправление URL для PostgreSQL на Heroku
database_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
if database_url and database_url.startswith("postgres://"):
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url.replace("postgres://", "postgresql://", 1)

db.init_app(app)

def fix_sequences():
    """Исправляет sequences для автоинкремента в PostgreSQL"""
    try:
        # Исправляем sequence для категорий
        result = db.session.execute(text("SELECT MAX(id) FROM category")).fetchone()
        max_id = result[0] if result and result[0] else 0
        db.session.execute(text(f"SELECT setval('category_id_seq', {max_id + 1})"))
        print(f"Fixed category_id_seq to {max_id + 1}")
        
        # Исправляем sequence для материалов
        result = db.session.execute(text("SELECT MAX(id) FROM materials")).fetchone()
        max_id = result[0] if result and result[0] else 0
        db.session.execute(text(f"SELECT setval('materials_id_seq', {max_id + 1})"))
        print(f"Fixed materials_id_seq to {max_id + 1}")
        
        # Исправляем sequence для брендов
        result = db.session.execute(text("SELECT MAX(id) FROM brands")).fetchone()
        max_id = result[0] if result and result[0] else 0
        db.session.execute(text(f"SELECT setval('brands_id_seq', {max_id + 1})"))
        print(f"Fixed brands_id_seq to {max_id + 1}")
        
        db.session.commit()
        print("All sequences fixed successfully!")
        
    except Exception as e:
        print(f"Error fixing sequences: {str(e)}")
        db.session.rollback()

def create_default_category():
    """Создает категорию 'Без категарії' если её нет"""
    try:
        from models import Category
        default_category = Category.query.filter_by(name='Без категарії').first()
        if not default_category:
            default_category = Category(name='Без категарії')
            db.session.add(default_category)
            db.session.commit()
            print("Created default category 'Без категарії'")
        else:
            print("Default category 'Без категарії' already exists")
    except Exception as e:
        print(f"Error creating default category: {str(e)}")
        db.session.rollback()

if __name__ == '__main__':
    with app.app_context():
        print("Applying database migrations...")
        try:
            upgrade()
            print("Migrations applied successfully!")
        except Exception as e:
            print(f"Error applying migrations: {str(e)}")
            # Если миграции не работают, создаем таблицы напрямую
            print("Trying to create tables directly...")
            try:
                db.create_all()
                print("Tables created successfully!")
            except Exception as e2:
                print(f"Error creating tables: {str(e2)}")
        
        # Исправляем sequences
        print("Fixing sequences...")
        fix_sequences()
        
        # Создаем категорию по умолчанию
        print("Creating default category...")
        create_default_category()
        
        print("Migration completed!") 