from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Конфигурация PostgreSQL
DB_HOST = '192.168.20.189'
DB_PORT = '5432'
DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_PASSWORD = '4578736'

# Строка подключения к PostgreSQL
SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Создаем движок базы данных
engine = create_engine(SQLALCHEMY_DATABASE_URI)

# Создаем базовый класс для моделей
Base = declarative_base()

# Создаем фабрику сессий
Session = sessionmaker(bind=engine) 