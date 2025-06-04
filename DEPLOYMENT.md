# 🚀 Деплой сайта portalabrams.com.ua

## 📋 Содержание
- [Рекомендуемые хостинг-провайдеры](#hosting)
- [Подготовка к деплою](#preparation)
- [Деплой на различные платформы](#deployment)
- [Настройка домена](#domain)
- [Автоматические обновления](#updates)
- [Мониторинг и бэкапы](#monitoring)

## 🏠 Рекомендуемые хостинг-провайдеры {#hosting}

### 💰 Бюджетные варианты (для начала):

#### 1. **Heroku** - Бесплатно/Дешево
- ✅ **Плюсы**: Простой деплой, автоматические обновления из Git
- ✅ **Цена**: $7/месяц за Hobby Dyno + PostgreSQL
- ✅ **Подходит**: Для тестирования и небольшой нагрузки
- 🔗 **Сайт**: [heroku.com](https://heroku.com)

#### 2. **PythonAnywhere** - $5/месяц
- ✅ **Плюсы**: Специализация на Python, простая настройка
- ✅ **Цена**: $5/месяц за Hacker план
- ✅ **Подходит**: Для небольших и средних проектов
- 🔗 **Сайт**: [pythonanywhere.com](https://pythonanywhere.com)

#### 3. **Railway** - $5/месяц
- ✅ **Плюсы**: Современная платформа, простой деплой
- ✅ **Цена**: $5/месяц + $5 за PostgreSQL
- ✅ **Подходит**: Альтернатива Heroku
- 🔗 **Сайт**: [railway.app](https://railway.app)

### 🚀 Производительные варианты:

#### 4. **DigitalOcean App Platform** - $12-25/месяц
- ✅ **Плюсы**: Хорошая производительность, масштабируемость
- ✅ **Цена**: $12/месяц за Basic + $15 за базу данных
- ✅ **Подходит**: Для стабильной работы под нагрузкой
- 🔗 **Сайт**: [digitalocean.com](https://digitalocean.com)

#### 5. **Украинские провайдеры**:
- **Ukraine.com.ua** - от $3/месяц
- **Hostiq.ua** - от $2/месяц  
- **1Gb.ua** - от $4/месяц
- ⚠️ **Примечание**: Убедитесь что поддерживают Python/Flask + PostgreSQL

## 📦 Подготовка к деплою {#preparation}

### 1. Создайте файл переменных окружения (.env):
```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/portalabrams

# Security Keys (generate your own!)
SECRET_KEY=your-very-secure-secret-key-here
WTF_CSRF_SECRET_KEY=your-csrf-secret-key-here

# Flask Environment  
FLASK_ENV=production
FLASK_DEBUG=False

# Domain
DOMAIN_NAME=portalabrams.com.ua
```

### 2. Генерация секретных ключей:
```python
# Запустите в Python консоли:
import secrets
print("SECRET_KEY:", secrets.token_urlsafe(32))
print("WTF_CSRF_SECRET_KEY:", secrets.token_urlsafe(32))
```

### 3. Обновите app.py для продакшена:
```python
# В начале app.py добавьте:
import os
if os.environ.get('FLASK_ENV') == 'production':
    from config_production import ProductionConfig
    app.config.from_object(ProductionConfig)
```

## 🚀 Деплой на Heroku (рекомендуем для начала) {#deployment}

### Шаг 1: Подготовка
```bash
# Установите Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Войдите в Heroku
heroku login

# Создайте приложение
heroku create portalabrams
```

### Шаг 2: Настройка базы данных
```bash
# Добавьте PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Посмотрите DATABASE_URL
heroku config:get DATABASE_URL
```

### Шаг 3: Настройка переменных
```bash
# Установите переменные окружения
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set WTF_CSRF_SECRET_KEY="your-csrf-key"
heroku config:set FLASK_ENV="production"
```

### Шаг 4: Деплой
```bash
# Отправьте код в Heroku
git push heroku main

# Выполните миграции
heroku run flask db upgrade

# Откройте сайт
heroku open
```

## 🌐 Настройка домена portalabrams.com.ua {#domain}

### Шаг 1: Покупка домена
1. Перейдите на [ukraine.com.ua](https://ukraine.com.ua) или [nic.ua](https://nic.ua)
2. Найдите и купите домен `portalabrams.com.ua`
3. Дождитесь подтверждения покупки

### Шаг 2: Настройка DNS (для Heroku)
```bash
# Добавьте домен в Heroku
heroku domains:add portalabrams.com.ua
heroku domains:add www.portalabrams.com.ua

# Получите адрес для DNS
heroku domains
```

### Шаг 3: Настройка DNS записей
В панели управления доменом добавьте:
```
Type: CNAME
Name: www
Value: [адрес из heroku domains]

Type: CNAME  
Name: @
Value: [адрес из heroku domains]
```

### Шаг 4: SSL сертификат
```bash
# Heroku автоматически выдаст SSL
heroku certs:auto:enable
```

## 🔄 Автоматические обновления {#updates}

### GitHub Actions для автодеплоя:
Создайте `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Heroku

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - uses: akhileshns/heroku-deploy@v3.12.12
      with:
        heroku_api_key: ${{secrets.HEROKU_API_KEY}}
        heroku_app_name: "portalabrams"
        heroku_email: "your-email@domain.com"
```

### Процесс обновления:
1. 💻 Вносите изменения в локальную версию
2. 📤 Отправляете в GitHub: `git push origin main`  
3. 🚀 Автоматический деплой на хостинг
4. ✅ Сайт обновляется через 2-3 минуты

## 📊 Мониторинг и бэкапы {#monitoring}

### Логи Heroku:
```bash
# Просмотр логов
heroku logs --tail

# Логи конкретного компонента
heroku logs --source app --tail
```

### Бэкап базы данных:
```bash
# Создание бэкапа
heroku pg:backups:capture

# Скачивание бэкапа
heroku pg:backups:download
```

### Мониторинг:
- 📈 **Heroku Metrics** - встроенная аналитика
- 🔍 **LogDNA/Papertrail** - для детальных логов
- 📊 **New Relic** - мониторинг производительности

## 💡 Полезные команды

### Heroku:
```bash
# Рестарт приложения
heroku restart

# Просмотр конфигурации
heroku config

# Запуск миграций
heroku run flask db upgrade

# Доступ к консоли
heroku run python
```

### Локальная разработка:
```bash
# Запуск в режиме разработки
python app.py

# Создание миграций
flask db migrate -m "описание изменений"

# Применение миграций
flask db upgrade
```

## 🆘 Решение проблем

### Ошибка "Application error":
```bash
# Проверьте логи
heroku logs --tail

# Убедитесь что все переменные установлены
heroku config
```

### Проблемы с базой данных:
```bash
# Проверьте подключение к БД
heroku pg:info

# Сброс базы данных (ОСТОРОЖНО!)
heroku pg:reset DATABASE_URL
heroku run flask db upgrade
```

### Проблемы с доменом:
1. Проверьте DNS записи (может занять до 24 часов)
2. Убедитесь что домен добавлен в Heroku
3. Проверьте SSL сертификат

---

## 🎯 Быстрый старт (за 30 минут):

1. **5 мин**: Регистрация на Heroku + установка CLI
2. **10 мин**: Создание приложения и настройка БД  
3. **5 мин**: Деплой кода
4. **10 мин**: Покупка и настройка домена

**Общая стоимость**: ~$15/месяц (Heroku + домен)

**Результат**: Полностью работающий сайт на portalabrams.com.ua с возможностью легких обновлений! 