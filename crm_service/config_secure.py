import os
from dotenv import load_dotenv

# Загружаем переменные из .env.crm файла
load_dotenv(dotenv_path='../.env.crm')

class Config:
    """Базовая конфигурация CRM"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-change-in-production'
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Database
    CRM_DB_HOST = os.environ.get('CRM_DB_HOST', 'localhost')
    CRM_DB_PORT = os.environ.get('CRM_DB_PORT', '5432')
    CRM_DB_USER = os.environ.get('CRM_DB_USER', 'postgres')
    CRM_DB_PASSWORD = os.environ.get('CRM_DB_PASSWORD', '')
    CRM_DB_NAME = os.environ.get('CRM_DB_NAME', 'crm_database')
    
    @property
    def DATABASE_URL(self):
        return f"postgresql://{self.CRM_DB_USER}:{self.CRM_DB_PASSWORD}@{self.CRM_DB_HOST}:{self.CRM_DB_PORT}/{self.CRM_DB_NAME}"
    
    # Security
    ALLOWED_IPS_RAW = os.environ.get('ALLOWED_IPS', '127.0.0.1,192.168.20.0/24,172.18.0.0/16')
    ALLOWED_IPS = [ip.strip() for ip in ALLOWED_IPS_RAW.split(',')]
    
    # Debug
    print(f"DEBUG CONFIG: ALLOWED_IPS_RAW = {ALLOWED_IPS_RAW}")
    print(f"DEBUG CONFIG: ALLOWED_IPS = {ALLOWED_IPS}")
    
    # Rate limiting
    MAX_RECORDS_PER_REQUEST = 100
    
class DevelopmentConfig(Config):
    """Конфигурация для разработки"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Конфигурация для продакшена"""
    DEBUG = False
    MAX_RECORDS_PER_REQUEST = 50

# Выбор конфигурации
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 