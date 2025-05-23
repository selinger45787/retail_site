# Навчальна платформа

Веб-додаток для навчання та тестування співробітників з матеріалів про бренди та продукцію.

## Функціональність

- Авторизація користувачів (адміністратори та звичайні користувачі)
- Управління брендами та матеріалами
- Створення та призначення тестів
- Проходження тестів та відстеження результатів
- Адміністративна панель зі статистикою

## Технології

- Python 3.x
- Flask
- SQLAlchemy
- PostgreSQL
- Bootstrap 5
- JavaScript

## Встановлення

1. Клонуйте репозиторій:
```bash
git clone https://github.com/your-username/retail_site.git
cd retail_site
```

2. Створіть віртуальне середовище та встановіть залежності:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows
pip install -r requirements.txt
```

3. Налаштуйте змінні середовища:
```bash
cp .env.example .env
# Відредагуйте .env файл з вашими налаштуваннями
```

4. Ініціалізуйте базу даних:
```bash
flask db upgrade
```

5. Запустіть додаток:
```bash
flask run
```

## Структура проекту

```
retail_site/
├── app.py              # Головний файл додатку
├── config.py           # Конфігурація
├── forms.py            # Форми
├── models.py           # Моделі бази даних
├── requirements.txt    # Залежності
├── static/            # Статичні файли (CSS, JS, зображення)
└── templates/         # HTML шаблони
```

## Ліцензія

MIT 