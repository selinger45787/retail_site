#!/usr/bin/env python3
"""
Скрипт для отладки проблем на Heroku
"""
import os
import logging
from flask import Flask
from models import db, Material, Test, TestResult, MaterialView, TestAssignment

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Настройка для Heroku
environment = os.getenv('FLASK_ENV', 'development')
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

def check_database_tables():
    """Проверяет наличие всех необходимых таблиц"""
    with app.app_context():
        try:
            # Проверяем основные таблицы
            material_count = Material.query.count()
            logger.info(f"Materials table exists. Count: {material_count}")
            
            test_count = Test.query.count()
            logger.info(f"Tests table exists. Count: {test_count}")
            
            try:
                result_count = TestResult.query.count()
                logger.info(f"TestResults table exists. Count: {result_count}")
            except Exception as e:
                logger.error(f"TestResults table error: {str(e)}")
            
            try:
                view_count = MaterialView.query.count()
                logger.info(f"MaterialView table exists. Count: {view_count}")
            except Exception as e:
                logger.error(f"MaterialView table error: {str(e)}")
            
            try:
                assignment_count = TestAssignment.query.count()
                logger.info(f"TestAssignment table exists. Count: {assignment_count}")
            except Exception as e:
                logger.error(f"TestAssignment table error: {str(e)}")
                
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")

if __name__ == '__main__':
    check_database_tables() 