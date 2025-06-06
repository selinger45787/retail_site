#!/usr/bin/env python3
"""
Скрипт для применения миграций на Heroku
"""
import os
from flask import Flask
from flask_migrate import upgrade
from models import db

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