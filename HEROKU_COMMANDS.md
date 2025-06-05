# 🚀 Шпаргалка команд для деплоя на Heroku

## Быстрый деплой (копируйте и выполняйте по порядку):

### 1. Логин и создание приложения:
```bash
heroku login
heroku create abbramsspace
heroku addons:create heroku-postgresql:hobby-dev
```

### 2. Генерация ключей:
```bash
python -c "import secrets; print('SECRET_KEY:', secrets.token_urlsafe(32)); print('WTF_CSRF_SECRET_KEY:', secrets.token_urlsafe(32))"
```

### 3. Установка переменных (замените ключи на свои):
```bash
heroku config:set SECRET_KEY="ваш-сгенерированный-ключ"
heroku config:set WTF_CSRF_SECRET_KEY="ваш-csrf-ключ"
heroku config:set FLASK_ENV="production"
```

### 4. Деплой:
```bash
cd C:\Users\andre\retail_site_working
git push heroku main
heroku run flask db upgrade
```

### 5. Создание админа (замените пароль):
```bash
heroku run python -c "
from app import app, db
from models import User
with app.app_context():
    admin = User(username='admin', email='admin@abbramsspace.com.ua', role='admin')
    admin.set_password('ВашПароль123')
    db.session.add(admin)
    db.session.commit()
    print('Админ создан!')
"
```

### 6. Проверка и настройка домена:
```bash
heroku open
heroku domains:add abbramsspace.com.ua
heroku domains:add www.abbramsspace.com.ua
heroku domains
heroku certs:auto:enable
```

## 📱 После покупки домена:
1. В панели управления доменом добавьте CNAME записи из вывода `heroku domains`
2. Домен активируется через 1-24 часа

## 🔧 Полезные команды:
```bash
heroku logs --tail          # Просмотр логов
heroku restart              # Перезапуск
heroku config              # Просмотр настроек
heroku pg:info             # Информация о базе данных
```

## 💰 Стоимость:
- Домен: ~$10-15/год
- Heroku Hobby: $7/месяц
- PostgreSQL: бесплатно
**Итого: ~$8/месяц + домен** 