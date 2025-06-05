# 🚀 Пошаговый деплой на Heroku с доменом abbramsspace.com.ua

## ✅ Уже готово:
- ✅ Аккаунт на Heroku создан
- ✅ Домен `abbramsspace.com.ua` покупается
- ✅ Код подготовлен к деплою

## 🎯 План действий (30-40 минут):

### Шаг 1: Установка и настройка Heroku CLI (5 минут)

1. **Скачайте Heroku CLI:**
   - Перейдите на https://devcenter.heroku.com/articles/heroku-cli
   - Скачайте для Windows и установите

2. **Проверьте установку:**
   ```bash
   heroku --version
   ```

3. **Войдите в аккаунт:**
   ```bash
   heroku login
   ```
   Откроется браузер для авторизации.

### Шаг 2: Создание приложения на Heroku (5 минут)

```bash
# Создайте приложение (имя должно быть уникальным)
heroku create abbramsspace

# Если имя занято, попробуйте:
# heroku create abbramsspace-portal
# heroku create abbramsspace-app
# или любое другое уникальное имя
```

### Шаг 3: Добавление базы данных PostgreSQL (2 минуты)

```bash
# Добавьте PostgreSQL базу данных (бесплатная версия)
heroku addons:create heroku-postgresql:hobby-dev

# Проверьте что база добавилась
heroku config:get DATABASE_URL
```

### Шаг 4: Генерация и установка секретных ключей (5 минут)

1. **Генерируйте ключи:**
   ```bash
   python -c "import secrets; print('SECRET_KEY:', secrets.token_urlsafe(32)); print('WTF_CSRF_SECRET_KEY:', secrets.token_urlsafe(32))"
   ```

2. **Скопируйте полученные ключи и установите переменные окружения:**
   ```bash
   # Замените YOUR_SECRET_KEY на сгенерированный ключ
   heroku config:set SECRET_KEY="YOUR_SECRET_KEY"
   heroku config:set WTF_CSRF_SECRET_KEY="YOUR_CSRF_KEY"
   heroku config:set FLASK_ENV="production"
   ```

### Шаг 5: Деплой кода (5 минут)

```bash
# Убедитесь что находитесь в папке проекта
cd C:\Users\andre\retail_site_working

# Отправьте код на Heroku
git push heroku main
```

**Процесс займет 2-5 минут.** Вы увидите логи сборки приложения.

### Шаг 6: Выполнение миграций базы данных (2 минуты)

```bash
# Создайте таблицы в базе данных
heroku run flask db upgrade
```

### Шаг 7: Создание администратора (3 минуты)

```bash
# Создайте администратора для доступа к панели управления
heroku run python -c "
from app import app, db
from models import User
with app.app_context():
    admin = User(username='admin', email='admin@abbramsspace.com.ua', role='admin')
    admin.set_password('Ваш_Пароль_123')  # Замените на свой пароль
    db.session.add(admin)
    db.session.commit()
    print('Администратор создан!')
"
```

### Шаг 8: Проверка работы сайта (2 минуты)

```bash
# Откройте сайт в браузере
heroku open
```

Сайт должен открыться по адресу типа `https://abbramsspace.herokuapp.com`

### Шаг 9: Привязка домена abbramsspace.com.ua (10 минут)

1. **Добавьте домен в Heroku:**
   ```bash
   heroku domains:add abbramsspace.com.ua
   heroku domains:add www.abbramsspace.com.ua
   
   # Получите DNS адрес для настройки
   heroku domains
   ```

2. **Настройте DNS записи в панели управления доменом:**
   
   В административной панели вашего регистратора домена добавьте:
   
   ```
   Тип: CNAME
   Имя: www
   Значение: [скопируйте из вывода heroku domains]
   
   Тип: CNAME
   Имя: @
   Значение: [скопируйте из вывода heroku domains]
   ```

3. **Включите автоматический SSL:**
   ```bash
   heroku certs:auto:enable
   ```

### Шаг 10: Настройка автоматического деплоя (5 минут)

1. **Получите API ключ Heroku:**
   - Зайдите на https://dashboard.heroku.com/account
   - Прокрутите до "API Key" 
   - Нажмите "Reveal" и скопируйте ключ

2. **Добавьте секреты в GitHub:**
   - Перейдите в ваш репозиторий https://github.com/selinger45787/retail_site
   - Settings → Secrets and variables → Actions
   - Нажмите "New repository secret"
   
   Добавьте два секрета:
   ```
   Name: HEROKU_API_KEY
   Secret: [ваш API ключ из Heroku]
   
   Name: HEROKU_EMAIL
   Secret: [ваш email на Heroku]
   ```

## 🎉 Результат:

После выполнения всех шагов у вас будет:
- ✅ Работающий сайт на `https://abbramsspace.herokuapp.com`
- ✅ Привязанный домен `https://abbramsspace.com.ua` (активируется через 1-24 часа)
- ✅ SSL сертификат
- ✅ Автоматические обновления при `git push origin main`

## 🔧 Полезные команды для управления:

```bash
# Просмотр логов
heroku logs --tail

# Перезапуск приложения
heroku restart

# Просмотр конфигурации
heroku config

# Создание бэкапа базы данных
heroku pg:backups:capture

# Доступ к консоли Python на сервере
heroku run python
```

## 🆘 Если что-то пошло не так:

1. **Ошибка при деплое:**
   ```bash
   heroku logs --tail
   ```

2. **Проблемы с базой данных:**
   ```bash
   heroku pg:info
   ```

3. **Сайт не открывается:**
   - Проверьте логи
   - Убедитесь что все переменные окружения установлены: `heroku config`

## 🔄 Процесс обновления сайта в будущем:

1. Вносите изменения в код локально
2. `git add .`
3. `git commit -m "описание изменений"`
4. `git push origin main`
5. GitHub Actions автоматически обновит сайт на Heroku

---

### 🚀 Готовы начать? Начинайте с Шага 1! 