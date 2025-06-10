# Техническое описание проекта: Навчальна платформа Abrams

## 🎯 Общее описание
Корпоративная обучающая платформа для компании Abrams - веб-приложение для управления учебными материалами, тестирования сотрудников и аналитики обучения. Система предоставляет многоуровневый доступ с административной панелью и пользовательским интерфейсом.

## 🏗️ Архитектура

### Паттерн: MVC (Model-View-Controller)
- **Model**: SQLAlchemy ORM модели (models.py)
- **View**: Jinja2 HTML шаблоны (templates/)
- **Controller**: Flask routes и business logic (app.py)

### Структура проекта:
```
retail_site_working/
├── app.py                     # Основное приложение Flask (3240 строк)
├── models.py                  # Модели базы данных (615 строк)
├── forms.py                   # WTForms формы (187 строк)
├── config.py                  # Конфигурация разработки
├── config_production.py       # Конфигурация продакшена
├── security_utils.py          # Утилиты безопасности (160 строк)
├── requirements.txt           # Зависимости
├── Procfile                   # Heroku deployment
├── runtime.txt                # Python версия для Heroku
├── templates/                 # HTML шаблоны Jinja2
│   ├── base.html             # Базовый шаблон
│   ├── admin/                # Административные шаблоны
│   ├── *.html                # Страницы пользователей
├── static/                    # Статические файлы
│   ├── css/style/            # CSS стили
│   ├── js/                   # JavaScript файлы
│   ├── img/                  # Изображения
│   └── uploads/              # Загруженные файлы
├── migrations/                # Flask-Migrate миграции БД
├── tests/                     # Тестовые данные
└── deploy files/              # Файлы деплоя (Heroku)
```

## 🛠️ Технологический стек

### Backend Framework
- **Flask 2.3.3** - основной web framework
- **Python 3.13** - язык программирования

### База данных
- **PostgreSQL** - основная БД (продакшен)
- **SQLite** - БД для разработки
- **Flask-SQLAlchemy 3.0.5** - ORM
- **Flask-Migrate 4.0.5** - миграции БД
- **psycopg2-binary 2.9.7** - PostgreSQL драйвер

### Аутентификация и безопасность
- **Flask-Login 0.6.3** - управление сессиями
- **Werkzeug 2.3.7** - хеширование паролей
- **Flask-WTF 1.1.1** - формы с CSRF защитой
- **Flask-CSRF 0.9.2** - дополнительная CSRF защита
- **bleach 6.0.0** - очистка HTML от XSS

### Формы и валидация
- **WTForms 3.0.1** - создание и валидация форм

### Файлы и изображения
- **Pillow 10.0.1** - обработка изображений
- **cloudinary 1.36.0** - облачное хранение изображений (опционально)

### Развертывание
- **gunicorn 21.2.0** - WSGI сервер для продакшена
- **Heroku** - платформа деплоя

### Утилиты
- **python-dotenv 1.0.0** - управление переменными окружения
- **MarkupSafe 2.1.3** - безопасная обработка разметки

### Frontend
- **Bootstrap 5.3.3** - CSS фреймворк
- **Font Awesome 6.5.1** - иконки
- **Chart.js 3.7.1** - графики и диаграммы
- **CKEditor 5** - WYSIWYG редактор
- **Custom CSS/JS** - собственные стили и скрипты

## 📊 Модель данных

### Основные сущности:

#### 1. User (Пользователи)
```python
- id: Integer (PK)
- username: String(80) (unique)
- password_hash: String(128)
- role: String(20) ['admin', 'user']
- phone_number: String(20)
- department: String(50) # отдел
- position: String(50) # должность
- photo_path: String(255) # фото для руководителей
- created_at: DateTime
```

**Отделы**: Засновники, Директор, Бухгалтерия, Маркетинг, Онлайн продажи, Офлайн продажи, ЗЕД, Склад, Аналитика, Виробництво Abrams

**Должности**: Засновник, Директор, Керівник відділу, Бухгалтер, Фотограф, Маркетолог, Менеджери, Продавець, Касир, та інші

#### 2. Brand (Бренды)
```python
- id: Integer (PK)
- name: String(100)
- image_path: String(200)
- created_at: DateTime
- materials: relationship -> Material
```

#### 3. Category (Категории)
```python
- id: Integer (PK)  
- name: String(100)
- materials: relationship -> Material
```

#### 4. Material (Учебные материалы)
```python
- id: Integer (PK)
- title: String(100)
- description: Text # HTML контент
- image_path: String(255) # главное изображение
- date: DateTime
- brand_id: Integer (FK)
- category_id: Integer (FK)
- images: relationship -> MaterialImage # доп. изображения
```

#### 5. MaterialImage (Дополнительные изображения)
```python
- id: Integer (PK)
- image_path: String(255)
- material_id: Integer (FK)
- created_at: DateTime
```

#### 6. Test (Тесты)
```python
- id: Integer (PK)
- material_id: Integer (FK)
- created_at: DateTime
- is_active: Boolean
- questions: relationship -> TestQuestion
```

#### 7. TestQuestion (Вопросы теста)
```python
- id: Integer (PK)
- test_id: Integer (FK)
- text: Text
- correct_answer: String(255)
- answers: relationship -> TestAnswer
```

#### 8. TestAnswer (Варианты ответов)
```python
- id: Integer (PK)
- question_id: Integer (FK)
- text: String(255)
```

#### 9. TestResult (Результаты тестов)
```python
- id: Integer (PK)
- user_id: Integer (FK)
- test_id: Integer (FK)
- score: Integer # баллы
- max_score: Integer # максимальные баллы
- started_at: DateTime
- time_taken: Integer # время в секундах
- created_at: DateTime
```

#### 10. TestQuestionResult (Детальные результаты)
```python
- id: Integer (PK)
- test_result_id: Integer (FK)
- question_id: Integer (FK)
- answer_given: String(255)
- is_correct: Boolean
```

#### 11. TestAssignment (Назначения тестов)
```python
- id: Integer (PK)
- user_id: Integer (FK) # кому назначен
- material_id: Integer (FK)
- start_date: DateTime
- end_date: DateTime  
- is_completed: Boolean
- created_by: Integer (FK) # кто назначил
```

#### 12. Order (Служебные распоряжения)
```python
- id: Integer (PK)
- title: String(200)
- description: Text # HTML контент
- number: String(50) # номер распоряжения
- departments: JSON # список отделов для видимости
- status: String(20) ['active', 'archived']
- author_id: Integer (FK)
- image_path: String(255)
- due_date_from/to: DateTime # период выполнения
```

#### 13. MaterialView (Аналитика просмотров)
```python
- id: Integer (PK)
- material_id: Integer (FK)
- user_id: Integer (FK)
- viewed_at: DateTime
- time_spent: Integer # время в секундах
- page_type: String(50) ['material', 'category', 'brand']
```

### Связи между сущностями:
- User ←→ TestResult (многие ко многим через результаты)
- User ←→ TestAssignment (многие ко многим через назначения)
- Brand → Material (один ко многим)
- Category → Material (один ко многим)
- Material → Test (один ко многим)
- Material → MaterialImage (один ко многим)
- Test → TestQuestion (один ко многим)
- TestQuestion → TestAnswer (один ко многим)
- Material ←→ User через MaterialView (аналитика)

## 🎨 Функциональность

### Пользовательские роли:

#### Обычный пользователь (role='user'):
- Просмотр учебных материалов по брендам/категориям
- Прохождение назначенных тестов
- Просмотр своих результатов тестирования
- Просмотр структуры компании
- Чтение служебных распоряжений
- Управление профилем

#### Администратор (role='admin'):
- Все функции пользователя +
- **Управление пользователями**: создание, редактирование, удаление, загрузка фото
- **Управление контентом**: создание/редактирование материалов, брендов, категорий
- **Управление тестами**: создание вопросов, назначение тестов пользователям
- **Аналитика**: детальная статистика тестирования, просмотров, проблемных областей
- **Служебные распоряжения**: создание, редактирование
- **Административная панель**: dashboard с графиками и аналитикой

### Основные страницы:

#### Публичные:
- `/` - Главная (список брендов)
- `/login` - Авторизация  
- `/brand/<id>` - Материалы бренда
- `/category/<id>` - Материалы категории
- `/material/<id>` - Просмотр материала
- `/company_structure` - Структура компании
- `/orders` - Служебные распоряжения

#### Пользовательские:
- `/user/profile` - Профиль пользователя
- `/material/<id>/test` - Прохождение теста
- `/my_assignments` - Назначенные тесты

#### Административные (prefix `/admin/`):
- `/admin/dashboard` - Главная панель с аналитикой
- `/admin/users` - Управление пользователями
- `/admin/add_user` - Добавление пользователя
- `/admin/brands` - Управление брендами
- `/admin/categories` - Управление категориями
- `/admin/materials` - Управление материалами
- `/admin/test_assignments` - Назначение тестов

## 🎨 Пользовательский интерфейс

### Дизайн системы:
- **Responsive design** - адаптивность под все устройства
- **Боковое меню** - навигация по брендам/категориям
- **Карточный интерфейс** - материалы отображаются в виде карточек
- **Модальные окна** - для форм и дополнительной информации
- **Цветовая схема**: оттенки серого, синие акценты
- **Иконки**: Font Awesome 6.5.1
- **Анимации**: плавные переходы, hover эффекты

### Ключевые UI компоненты:
- Система уведомлений (flash messages)
- Индикаторы загрузки
- Пагинация
- Поиск и фильтрация
- Drag & drop для загрузки файлов
- WYSIWYG редактор для контента
- Графики и диаграммы (Chart.js)

## 📁 Файловая система

### Загрузка файлов:
- **Изображения материалов**: `/static/img/materials/`
- **Изображения брендов**: `/static/img/brands/`
- **Фото пользователей**: `/static/img/users/`
- **Загрузки CKEditor**: `/static/uploads/`

### Безопасность файлов:
- Валидация MIME-типов
- Проверка расширений файлов
- Проверка магических байтов
- Ограничение размера (10MB)
- Безопасные имена файлов с временными метками

## 🔒 Безопасность

### Реализованные меры:
- **CSRF защита** на всех формах
- **XSS защита** через bleach и CSP заголовки
- **SQL инъекции** предотвращены через ORM
- **Аутентификация** через Flask-Login
- **Хеширование паролей** Werkzeug
- **Безопасные заголовки**: X-Frame-Options, X-Content-Type-Options и др.
- **Валидация загружаемых файлов**
- **Сессии** с HttpOnly и Secure флагами

### Content Security Policy:
```
default-src 'self';
script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net;
style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com;
img-src 'self' data: https: blob:;
font-src 'self' https://cdnjs.cloudflare.com;
```

## 📈 Аналитика и отчетность

### Типы аналитики:
1. **Статистика тестирования**:
   - Общее количество попыток
   - Средний балл по компании
   - Процент успешных тестов
   - Проблемные тесты (низкие баллы)
   - Проблемные пользователи

2. **Аналитика просмотров**:
   - Время, проведенное на материалах
   - Количество просмотров по брендам/категориям
   - Уникальные посетители
   - Популярные материалы

3. **Графики и визуализация**:
   - Chart.js диаграммы знаний по брендам
   - Таблицы с детальной статистикой
   - Цветовые индикаторы результатов

### Dashboard функции:
- Общая статистика (карточки с ключевыми метриками)
- График знаний по брендам
- Анализ проблемных областей
- Детальные результаты пользователей с раскрываемыми строками
- Поиск и сортировка пользователей
- Экспорт данных

## ⚙️ Конфигурация

### Переменные окружения:
```bash
# Обязательные
SECRET_KEY=<secure-random-key>
DATABASE_URL=<postgresql-url>
FLASK_ENV=production

# Опциональные
WTF_CSRF_SECRET_KEY=<csrf-key>
CLOUDINARY_CLOUD_NAME=<cloudinary-name>
CLOUDINARY_API_KEY=<cloudinary-key>
CLOUDINARY_API_SECRET=<cloudinary-secret>
```

### Конфигурации:
- **Development**: SQLite, DEBUG=True, Auto-reload
- **Production**: PostgreSQL, DEBUG=False, Secure cookies, HTTPS

## 🚀 Развертывание

### Платформы:
- **Heroku** - основная платформа (настроена)
- **Local development** - через Flask dev server
- **Production ready** - через Gunicorn

### Миграции БД:
- Автоматические через Flask-Migrate
- Скрипты для Heroku: `migrate_heroku.py`
- Исправление последовательностей PostgreSQL

### Файлы деплоя:
- `Procfile` - команды для Heroku
- `runtime.txt` - версия Python
- `requirements.txt` - зависимости
- Скрипты миграции и отладки

## 🧪 Тестирование

### Структура тестов:
- Тестовые данные в `/tests/`
- Скрипты импорта/экспорта данных
- Seed данные для разработки

## 📝 API и интеграции

### AJAX endpoints:
- `/upload-image` - загрузка изображений через CKEditor
- `/api/admin/user_tests/<user_id>` - получение результатов пользователя
- `/material/<id>/update_time` - отслеживание времени просмотра
- CRUD операции через формы

### Внешние сервисы:
- **Cloudinary** - облачное хранение изображений
- **CDN ресурсы**: Bootstrap, Font Awesome, Chart.js

## 🎯 Ключевые особенности

1. **Многоуровневый доступ** - пользователи и администраторы
2. **Организационная структура** - отделы и должности
3. **Система тестирования** - с назначениями и аналитикой  
4. **Rich content** - WYSIWYG редактор с изображениями
5. **Аналитика в реальном времени** - отслеживание активности
6. **Responsive design** - работает на всех устройствах
7. **Безопасность** - современные стандарты защиты
8. **Масштабируемость** - готов к росту пользователей

Система полностью готова к продакшену и активно используется для корпоративного обучения в компании Abrams. 