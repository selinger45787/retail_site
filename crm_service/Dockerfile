FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Создание requirements.txt для CRM
COPY requirements.txt* ./
RUN echo "Flask==2.3.3" > requirements.txt && \
    echo "Flask-SQLAlchemy>=2.5.0,<3.1.0" >> requirements.txt && \
    echo "SQLAlchemy>=1.4.0,<2.0.0" >> requirements.txt && \
    echo "psycopg2-binary" >> requirements.txt && \
    echo "Flask-CORS" >> requirements.txt && \
    echo "python-dotenv" >> requirements.txt

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода CRM
COPY . .

# Открытие порта
EXPOSE 5001

# Переменные окружения
ENV FLASK_ENV=development

# Команда запуска
CMD ["python", "secure_crm.py"]