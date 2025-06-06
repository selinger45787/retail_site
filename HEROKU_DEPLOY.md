# Развертывание на Heroku

## Пошаговая инструкция

### 1. Подготовка к деплою

```bash
# Убедитесь, что все изменения закоммичены
git add .
git commit -m "Fix material deletion and add error handling"
git push origin main
```

### 2. Деплой на Heroku

```bash
# Деплой на Heroku (автоматически через GitHub)
# Или через Heroku CLI:
git push heroku main
```

### 3. Запуск миграций на Heroku

```bash
# Применить миграции базы данных
heroku run python migrate_heroku.py

# Или создать таблицы напрямую если миграции не работают
heroku run python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Tables created successfully!')
"
```

### 4. Проверка состояния базы данных

```bash
# Проверить наличие таблиц
heroku run python heroku_debug.py

# Проверить логи
heroku logs --tail
```

### 5. Диагностика проблем

Если удаление материалов не работает:

1. **Проверьте логи Heroku:**
   ```bash
   heroku logs --tail
   ```

2. **Проверьте наличие таблиц:**
   ```bash
   heroku run python heroku_debug.py
   ```

3. **Пересоздайте таблицы если нужно:**
   ```bash
   heroku run python -c "
   from app import app, db
   from models import MaterialView, TestResult
   with app.app_context():
       db.create_all()
       print('All tables created!')
   "
   ```

## Основные изменения в коде

- ✅ Добавлена защита от ошибок при работе с `MaterialView` и `TestResult` таблицами
- ✅ Исправлено дублирование удаления записей
- ✅ Добавлено детальное логирование для отладки
- ✅ Добавлена мягкая обработка ошибок базы данных
- ✅ Создан скрипт проверки состояния БД (`heroku_debug.py`)
- ✅ Создан скрипт миграций (`migrate_heroku.py`)

## Возможные проблемы и решения

### Ошибка 500 при удалении материала
**Причина:** Отсутствуют таблицы `MaterialView` или `TestResult`
**Решение:** Запустить `heroku run python migrate_heroku.py`

### Ошибка при обновлении времени просмотра
**Причина:** Таблица `MaterialView` не создана
**Решение:** Запустить создание таблиц напрямую через `db.create_all()`

### CSRF ошибки
**Причина:** Неправильная передача CSRF токена
**Решение:** Проверить что CSRF токен передается в JavaScript запросах 