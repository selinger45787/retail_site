import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv('.flaskenv')

class Config:
    # Основные настройки Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Настройки базы данных - ПРИНУДИТЕЛЬНО POSTGRESQL!
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/postgres')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Настройки для разработки
    TEMPLATES_AUTO_RELOAD = DEBUG
    SEND_FILE_MAX_AGE_DEFAULT = 0 if DEBUG else 3600
    
    # Настройки загрузки файлов
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Настройки безопасности
    SESSION_COOKIE_SECURE = False  # Отключаем для разработки
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'  # Более мягкие настройки
    REMEMBER_COOKIE_SECURE = False
    REMEMBER_COOKIE_HTTPONLY = True

class DevelopmentConfig(Config):
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True

class ProductionConfig(Config):
    DEBUG = False
    TEMPLATES_AUTO_RELOAD = False

# Выбор конфигурации в зависимости от окружения
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 