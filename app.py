from flask import Flask, render_template, redirect, url_for, request, flash, send_from_directory, jsonify, current_app, session
import os
import markupsafe
from models import db, User, Brand, Material, Category, MaterialImage, Test, TestQuestion, TestAnswer, TestResult, TestQuestionResult, TestAssignment, Order, MaterialView
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import logging
from config import config
from datetime import datetime, timedelta
from flask_migrate import Migrate
import bleach
from html import unescape
from flask_wtf.csrf import CSRFProtect, validate_csrf
import traceback
import psycopg2
import decimal
from forms import AddUserForm, LoginForm, TestAssignmentForm, EditTestAssignmentForm, EditUserForm
from functools import wraps
import re
from security_utils import validate_image_file, generate_secure_filename

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация приложения
app = Flask(__name__)

# Настройки конфигурации в зависимости от окружения
environment = os.getenv('FLASK_ENV', 'development')
if environment == 'production':
    from config_production import ProductionConfig
    app.config.from_object(ProductionConfig)
else:
    app.config.from_object(config['development'])

# Исправление URL для PostgreSQL на Heroku
database_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
if database_url and database_url.startswith("postgres://"):
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url.replace("postgres://", "postgresql://", 1)
    logger.info(f"Fixed database URL from postgres:// to postgresql://")

# Инициализация CSRF-защиты
csrf = CSRFProtect()
csrf.init_app(app)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('У вас нет прав для доступа к этой странице', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Контекстный процессор для передачи брендов во все шаблоны
@app.context_processor
def inject_brands():
    try:
        brands = Brand.query.all()
        return dict(brands=brands)
    except Exception as e:
        db.session.rollback()  # Откатываем транзакцию в случае ошибки
        logger.error(f"Error loading brands: {str(e)}")
        return dict(brands=[])

# Создаем необходимые папки
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.static_folder, 'img', 'materials'), exist_ok=True)
os.makedirs(os.path.join(app.static_folder, 'img', 'brands'), exist_ok=True)
os.makedirs(os.path.join(app.static_folder, 'img', 'icons'), exist_ok=True)
os.makedirs(os.path.join(app.static_folder, 'uploads'), exist_ok=True)  # Папка для загружаемых изображений из CKEditor
os.makedirs(os.path.join(app.root_path, 'tests'), exist_ok=True)  # Папка для CSV файлов с тестами

# Добавляем отладочный вывод для проверки путей
logger.info(f"Static folder: {app.static_folder}")
logger.info(f"Static URL path: {app.static_url_path}")

# Инициализация расширений
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Настройка разрешенных HTML-тегов и атрибутов
ALLOWED_TAGS = ['p', 'br', 'b', 'i', 'em', 'strong', 'a', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    '*': ['class']
}

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error loading user: {str(e)}")
        return None

@app.context_processor
def inject_user_and_brands():
    try:
        brands = Brand.query.order_by(Brand.name).all()
        categories = Category.query.order_by(Category.name).all()
        return {
            'current_user': current_user,
            'brands': brands,
            'categories': categories
        }
    except Exception as e:
        db.session.rollback()  # Откатываем транзакцию в случае ошибки
        logger.error(f"Error loading brands and categories: {str(e)}")
        return {
            'current_user': current_user,
            'brands': [],
            'categories': []
        }

@app.route('/static/img/materials/<path:filename>')
def serve_material_image(filename):
    try:
        # Сначала пробуем найти файл в папке materials
        file_path = os.path.join(app.static_folder, 'img', 'materials', filename)
        logger.info(f"Пытаемся найти файл: {file_path}")
        
        if os.path.exists(file_path):
            logger.info(f"Файл найден: {file_path}")
            return send_from_directory(os.path.join(app.static_folder, 'img', 'materials'), filename)
        
        # Если файл не найден, возвращаем изображение по умолчанию
        default_path = os.path.join(app.static_folder, 'img', 'materials', 'default.png')
        logger.info(f"Файл {filename} не найден, используем изображение по умолчанию: {default_path}")
        
        if os.path.exists(default_path):
            return send_from_directory(os.path.join(app.static_folder, 'img', 'materials'), 'default.png')
        else:
            logger.error(f"Файл по умолчанию не найден: {default_path}")
            return "File not found", 404
            
    except Exception as e:
        logger.error(f"Ошибка при загрузке изображения {filename}: {str(e)}")
        return "Internal server error", 500

def nl2br(value):
    if not value:
        return ''
    return markupsafe.Markup(value.replace('\n', '<br>'))

def safe_html(value):
    """Фільтр для безпечного відображення HTML контенту"""
    if not value:
        return ''
    # Використовуємо bleach для очищення HTML від небезпечних тегів
    allowed_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'br', 'b', 'i', 'em', 'strong', 'u', 'ul', 'ol', 'li', 'a']
    allowed_attributes = {'a': ['href', 'title']}
    clean_html = bleach.clean(value, tags=allowed_tags, attributes=allowed_attributes, strip=True)
    return markupsafe.Markup(clean_html)

def replace_drive_links_with_images(text):
    """Фільтр для автоматичної заміни посилань Google Drive на зображення"""
    if not text:
        return ""

    # Знайти всі посилання виду drive.google.com/file/d/FILE_ID/view...
    pattern = r'https:\/\/drive\.google\.com\/file\/d\/([a-zA-Z0-9_-]+)\/view[^\s"<]*'
    
    def replacer(match):
        file_id = match.group(1)
        direct_link = f'https://drive.google.com/uc?export=view&id={file_id}'
        return f'<img src="{direct_link}" alt="Google Drive Image" class="img-fluid my-2" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">'

    result = re.sub(pattern, replacer, text)
    return markupsafe.Markup(result)

app.jinja_env.filters['nl2br'] = nl2br
app.jinja_env.filters['safe_html'] = safe_html
app.jinja_env.filters['replace_drive_links_with_images'] = replace_drive_links_with_images

def get_score_color_class(score):
    """Возвращает CSS класс для цветового форматирования балла"""
    if score >= 80:
        return 'score-excellent'
    elif score >= 60:
        return 'score-good'
    else:
        return 'score-poor'

app.jinja_env.filters['score_color'] = get_score_color_class

@app.route('/')
def index():
    brands = Brand.query.all()
    
    # Получаем назначенные тесты для текущего пользователя
    assigned_tests = []
    if current_user.is_authenticated:
        now = datetime.utcnow()  # Используем UTC время
        assignments = TestAssignment.query.filter(
            TestAssignment.user_id == current_user.id,
            TestAssignment.is_completed == False,
            TestAssignment.end_date >= now
        ).order_by(TestAssignment.end_date).all()
        
        for assignment in assignments:
            material = Material.query.get(assignment.material_id)
            if material:
                brand = Brand.query.get(material.brand_id)
                assigned_tests.append({
                    'material': material,
                    'brand': brand,
                    'start_date': assignment.start_date,
                    'end_date': assignment.end_date,
                    'is_active': assignment.start_date <= now <= assignment.end_date
                })
    
    return render_template('index.html', 
                         brands=brands,
                         assigned_tests=assigned_tests,
                         now=datetime.utcnow())  # Передаем now в шаблон

@app.route('/brand/<int:brand_id>')
def brand(brand_id):
    brand = Brand.query.get_or_404(brand_id)
    page = request.args.get('page', 1, type=int)
    per_page = 12  # Кількість матеріалів на сторінці
    
    # Получаем материалы с пагинацией, сортируем по дате в обратном порядке
    materials_pagination = Material.query.filter_by(brand_id=brand_id)\
        .order_by(Material.id.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    # Получаем все категории для фильтрации
    categories = Category.query.all()
    
    return render_template('brand.html', 
                         brand=brand, 
                         materials=materials_pagination.items,
                         pagination=materials_pagination,
                         categories=categories)

@app.route('/brand/<int:brand_id>/info')
def brand_info(brand_id):
    brand = Brand.query.get_or_404(brand_id)
    return render_template('brand_info.html', brand=brand)

@app.route('/brand/<int:brand_id>/history')
def brand_history(brand_id):
    brand = Brand.query.get_or_404(brand_id)
    return render_template('brand_history.html', brand=brand)

@app.route('/mission')
@login_required
def mission():
    return render_template('mission.html')

@app.route('/add_material', defaults={'brand_id': None}, methods=['GET', 'POST'])
@app.route('/brand/<int:brand_id>/add_material', methods=['GET', 'POST'])
def add_material(brand_id):
    categories = Category.query.all()
    brands = Brand.query.all()
    
    # Получаем category_id из параметров URL
    preselected_category_id = request.args.get('category_id', type=int)
    
    if request.method == 'POST':
        logger.info("Получен POST запрос на добавление материала")
        logger.info(f"Form data: {request.form}")
        logger.info(f"Files: {request.files}")
        
        title = request.form.get('title')
        raw_description = request.form.get('description') or ''
        description = unescape(raw_description)
        
        logger.info("=== Декодирование HTML ===")
        logger.info(f"Исходный HTML: {raw_description}")
        logger.info(f"Декодированный HTML: {description}")
        logger.info("========================")
        
        category_id = request.form.get('category_id')
        main_image = request.files.get('image')
        additional_images = request.files.getlist('additional_images')
        
        logger.info(f"Полученные данные: title={title}, category_id={category_id}")
        logger.info(f"Описание материала (raw): {raw_description}")
        
        # Если brand_id не передан в URL, берем его из формы
        if brand_id is None:
            brand_id = request.form.get('brand_id')
            logger.info(f"brand_id из формы: {brand_id}")
        
        if not all([title, description, category_id, brand_id]):
            missing_fields = []
            if not title: missing_fields.append('title')
            if not description: missing_fields.append('description')
            if not category_id: missing_fields.append('category_id')
            if not brand_id: missing_fields.append('brand_id')
            logger.error(f"Відсутні обов'язкові поля: {missing_fields}")
            if request.headers.get('Accept') == 'application/json':
                return jsonify({'error': 'Будь ласка, заповніть всі обов\'язкові поля'}), 400
            flash('Будь ласка, заповніть всі обов\'язкові поля', 'error')
            return redirect(url_for('add_material', brand_id=brand_id, category_id=preselected_category_id))
        
        try:
            # Сохраняем главное изображение
            main_image_path = None
            if main_image and main_image.filename:
                filename = generate_secure_filename(main_image.filename)
                image_path = os.path.join(app.static_folder, 'img', 'materials', filename)
                main_image.save(image_path)
                main_image_path = filename
                logger.info(f"Сохранено главное изображение: {filename}")
            
            # Создаем новый материал
            logger.info("=== Начало создания материала ===")
            logger.info(f"Заголовок: {title}")
            logger.info(f"Описание (raw): {raw_description}")
            logger.info(f"Описание (тип): {type(raw_description)}")
            logger.info(f"Описание (длина): {len(raw_description) if raw_description else 0}")
            
            material = Material(
                title=title,
                description=description,  # Сохраняем HTML как есть
                image_path=main_image_path,
                brand_id=brand_id,
                category_id=category_id
            )
            
            db.session.add(material)
            db.session.flush()
            logger.info(f"Создан новый материал с ID: {material.id}")
            logger.info(f"Сохраненное описание: {material.description}")
            logger.info(f"Сохраненное описание (тип): {type(material.description)}")
            logger.info("=== Конец создания материала ===")
            
            # Сохраняем дополнительные изображения
            for image in additional_images:
                if image and image.filename:
                    filename = generate_secure_filename(image.filename)
                    image_path = os.path.join(app.static_folder, 'img', 'materials', filename)
                    image.save(image_path)
                    
                    material_image = MaterialImage(
                        image_path=filename,
                        material_id=material.id
                    )
                    db.session.add(material_image)
            
            db.session.commit()
            logger.info("Материал успешно сохранен в базу данных")
            
            if request.headers.get('Accept') == 'application/json':
                return jsonify({
                    'success': True,
                    'redirect': url_for('brand', brand_id=brand_id) if brand_id else url_for('category', category_id=category_id)
                })
            
            flash('Матеріал успішно додано', 'success')
            
            # Перенаправляем на страницу категории, если пришли с категории
            if preselected_category_id:
                return redirect(url_for('category', category_id=preselected_category_id))
            else:
                return redirect(url_for('brand', brand_id=brand_id))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Ошибка при сохранении материала: {str(e)}")
            if request.headers.get('Accept') == 'application/json':
                return jsonify({'error': 'Помилка при додаванні матеріалу'}), 500
            flash('Помилка при додаванні матеріалу', 'error')
            return redirect(url_for('add_material', brand_id=brand_id, category_id=preselected_category_id))
    
    # Для GET запроса
    brand = None
    if brand_id:
        brand = Brand.query.get_or_404(brand_id)
    
    return render_template('material_add.html', 
                         brand=brand,
                         brands=brands,
                         categories=categories,
                         preselected_category_id=preselected_category_id,
                         show_brand_select=brand_id is None)

@app.route('/material/<int:material_id>')
def view_material(material_id):
    material = Material.query.get_or_404(material_id)
    images = MaterialImage.query.filter_by(material_id=material_id).all()
    
    # Определяем источник перехода
    from_admin = request.args.get('from') == 'admin'
    
    # Отслеживаем просмотр материала (только для авторизованных пользователей)
    if current_user.is_authenticated:
        try:
            # Проверяем, есть ли уже запись о просмотре этого материала этим пользователем сегодня
            today = datetime.utcnow().date()
            existing_view = MaterialView.query.filter(
                MaterialView.material_id == material_id,
                MaterialView.user_id == current_user.id,
                db.func.date(MaterialView.viewed_at) == today
            ).first()
            
            if not existing_view:
                # Создаем новую запись о просмотре
                view_record = MaterialView(
                    material_id=material_id,
                    user_id=current_user.id,
                    viewed_at=datetime.utcnow(),
                    page_type='material'
                )
                db.session.add(view_record)
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Ошибка при записи просмотра материала: {str(e)}")
    
    return render_template('material.html', 
                         material=material, 
                         images=images,
                         from_admin=from_admin)

@app.route('/material/<int:material_id>/update_time', methods=['POST'])
@login_required
def update_view_time(material_id):
    """API для обновления времени просмотра материала"""
    try:
        data = request.get_json()
        time_spent = data.get('time_spent', 0)
        
        if time_spent <= 0:
            return jsonify({'success': False, 'error': 'Invalid time'}), 400
        
        # Ищем сегодняшнюю запись просмотра
        today = datetime.utcnow().date()
        try:
            view_record = MaterialView.query.filter(
                MaterialView.material_id == material_id,
                MaterialView.user_id == current_user.id,
                db.func.date(MaterialView.viewed_at) == today
            ).first()
        except Exception as e:
            logger.warning(f"MaterialView table not accessible: {str(e)}")
            return jsonify({'success': False, 'error': 'MaterialView table error'}), 500
        
        if view_record:
            # Обновляем время просмотра
            view_record.time_spent = time_spent
            db.session.commit()
            return jsonify({'success': True})
        else:
            # Создаем новую запись, если не найдена
            view_record = MaterialView(
                material_id=material_id,
                user_id=current_user.id,
                viewed_at=datetime.utcnow(),
                time_spent=time_spent,
                page_type='material'
            )
            db.session.add(view_record)
            db.session.commit()
            return jsonify({'success': True})
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"Ошибка при обновлении времени просмотра: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/material/<int:material_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_material(material_id):
    material = Material.query.get_or_404(material_id)
    
    # Проверяем права доступа (пока только для админа)
    if not current_user.is_authenticated or current_user.role != 'admin':
        flash('У вас немає прав для редагування цього матеріалу', 'error')
        return redirect(url_for('view_material', material_id=material.id))
    
    if request.method == 'POST':
        try:
            # Обновляем основные данные
            material.title = request.form.get('title')
            material.description = request.form.get('description')
            material.category_id = request.form.get('category_id')
            
            # Обрабатываем главное изображение
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename:
                    filename = generate_secure_filename(file.filename)
                    file_path = os.path.join(app.static_folder, 'img', 'materials', filename)
                    file.save(file_path)
                    material.image_path = filename
            
            # Обрабатываем дополнительные изображения
            if 'additional_images' in request.files:
                files = request.files.getlist('additional_images')
                for file in files:
                    if file and file.filename:
                        filename = generate_secure_filename(file.filename)
                        file_path = os.path.join(app.static_folder, 'img', 'materials', filename)
                        file.save(file_path)
                        
                        material_image = MaterialImage(
                            image_path=filename,
                            material_id=material.id
                        )
                        db.session.add(material_image)
            
            db.session.commit()
            flash('Матеріал успішно оновлено', 'success')
            return redirect(url_for('view_material', material_id=material.id))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Помилка при оновленні матеріалу: {str(e)}")
            flash('Помилка при оновленні матеріалу', 'error')
    
    # Для GET запроса
    categories = Category.query.all()
    return render_template('material_edit.html', material=material, categories=categories)

@app.route('/material/<int:material_id>/delete', methods=['POST'])
@login_required
def delete_material(material_id):
    logger.info(f"=== Начало удаления материала {material_id} ===")
    try:
        logger.info(f"Пользователь: {current_user.username}, роль: {current_user.role}")
        
        if current_user.role != 'admin':
            logger.warning(f"Попытка удаления материала {material_id} пользователем без прав админа")
            return jsonify({'error': 'У вас немає прав для видалення матеріалів', 'redirect': url_for('view_material', material_id=material_id)}), 403

        # Получаем CSRF-токен из JSON-данных
        data = request.get_json()
        logger.info(f"Полученные данные: {data}")
        logger.info(f"Content-Type: {request.content_type}")
        logger.info(f"Headers: {dict(request.headers)}")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request URL: {request.url}")
        
        if not data or 'csrf_token' not in data:
            logger.error("CSRF token missing")
            return jsonify({'error': 'CSRF token missing'}), 400

        try:
            logger.info("Валидация CSRF токена...")
            validate_csrf(data['csrf_token'])
            logger.info("CSRF токен валидный")
        except Exception as e:
            logger.error(f"CSRF validation error: {str(e)}")
            logger.error(f"CSRF токен из запроса: {data.get('csrf_token', 'НЕТ')}")
            return jsonify({'error': 'Invalid CSRF token'}), 400

        # Проверяем существование материала
        material = Material.query.get(material_id)
        if not material:
            logger.error(f"Материал {material_id} не найден")
            return jsonify({'error': 'Матеріал не знайдено'}), 404

        brand_id = material.brand_id
        logger.info(f"Материал найден: {material.title}")

        # Проверяем наличие теста
        test = Test.query.filter_by(material_id=material_id).first()
        has_test = test is not None
        logger.info(f"Наличие теста: {has_test}")

        # Проверяем наличие активных назначений
        active_assignments = TestAssignment.query.filter_by(material_id=material_id, is_completed=False).count()
        has_active_assignments = active_assignments > 0
        logger.info(f"Активных назначений: {active_assignments}")

        # Проверяем наличие результатов тестов
        test_results_count = 0
        has_test_results = False
        if test:
            try:
                test_results_count = TestResult.query.filter_by(test_id=test.id).count()
                has_test_results = test_results_count > 0
                logger.info(f"Результатов тестов: {test_results_count}")
            except Exception as e:
                logger.warning(f"Ошибка при проверке результатов тестов: {str(e)}")
                test_results_count = 0
                has_test_results = False

        # Если это первый запрос на удаление, проверяем наличие зависимостей
        if not data.get('confirmed'):
            logger.info("Проверяем зависимости")
            
            # Если нет зависимостей, удаляем сразу
            if not has_test and not has_active_assignments and not has_test_results:
                logger.info("Зависимостей нет, удаляем материал сразу")
                try:
                    # Удаляем изображения
                    if material.image_path:
                        try:
                            image_path = os.path.join(app.static_folder, 'img', 'materials', material.image_path)
                            logger.info(f"Удаляем главное изображение: {image_path}")
                            if os.path.exists(image_path):
                                os.remove(image_path)
                        except Exception as e:
                            logger.warning(f"Ошибка при удалении главного изображения: {e}")

                    for image in material.images:
                        try:
                            image_path = os.path.join(app.static_folder, 'img', 'materials', image.image_path)
                            logger.info(f"Удаляем дополнительное изображение: {image_path}")
                            if os.path.exists(image_path):
                                os.remove(image_path)
                        except Exception as e:
                            logger.warning(f"Ошибка при удалении дополнительного изображения: {e}")

                    # Удаляем все записи просмотров материала
                    try:
                        MaterialView.query.filter_by(material_id=material_id).delete()
                        logger.info("Записи просмотров материала удалены")
                    except Exception as e:
                        logger.warning(f"Ошибка при удалении записей просмотров: {str(e)}")

                    # Удаляем результаты тестов
                    if test:
                        try:
                            TestResult.query.filter_by(test_id=test.id).delete()
                            logger.info("Результаты тестов удалены")
                        except Exception as e:
                            logger.warning(f"Ошибка при удалении результатов тестов: {str(e)}")

                    # Удаляем сам материал
                    logger.info("Удаляем материал из базы данных")
                    db.session.delete(material)
                    db.session.commit()
                    logger.info("Материал успешно удален")

                    # Добавляем флеш-сообщение
                    flash('Матеріал було успішно видалено', 'success')
                    
                    return jsonify({
                        'success': True,
                        'redirect': url_for('brand', brand_id=brand_id),
                        'message': 'Матеріал було успішно видалено'
                    })

                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Ошибка при удалении материала: {str(e)}")
                    return jsonify({
                        'error': 'Помилка при видаленні матеріалу',
                        'details': str(e)
                    }), 500
            
            # Если есть зависимости, возвращаем информацию о них
            logger.info("Есть зависимости, возвращаем информацию")
            return jsonify({
                'has_test': has_test,
                'has_active_assignments': has_active_assignments,
                'active_assignments_count': active_assignments,
                'has_test_results': has_test_results,
                'test_results_count': test_results_count,
                'needs_confirmation': True
            })

        # Если пользователь подтвердил удаление
        if data.get('confirmed'):
            logger.info("Начинаем процесс удаления")
            try:
                # Сначала удаляем все связанные результаты тестов
                if test:
                    logger.info("Удаляем связанные результаты теста")
                    try:
                        # Удаляем результаты вопросов теста
                        TestQuestionResult.query.filter(
                            TestQuestionResult.test_result_id.in_(
                                TestResult.query.filter_by(test_id=test.id).with_entities(TestResult.id)
                            )
                        ).delete(synchronize_session=False)
                        
                        # Удаляем результаты тестов
                        TestResult.query.filter_by(test_id=test.id).delete()
                        
                        # Удаляем ответы на вопросы
                        TestAnswer.query.filter(
                            TestAnswer.question_id.in_(
                                TestQuestion.query.filter_by(test_id=test.id).with_entities(TestQuestion.id)
                            )
                        ).delete(synchronize_session=False)
                        
                        # Удаляем вопросы теста
                        TestQuestion.query.filter_by(test_id=test.id).delete()
                        
                        # Удаляем сам тест
                        db.session.delete(test)
                        logger.info("Тест успешно удален")
                    except Exception as e:
                        logger.warning(f"Ошибка при удалении теста: {str(e)}")
                        # Пытаемся удалить тест альтернативным способом
                        try:
                            db.session.delete(test)
                            logger.info("Тест удален упрощенным способом")
                        except Exception as e2:
                            logger.error(f"Не удалось удалить тест: {str(e2)}")

                # Удаляем все назначения теста
                TestAssignment.query.filter_by(material_id=material_id).delete()
                logger.info("Назначения теста удалены")

                # Удаляем все записи просмотров материала
                try:
                    MaterialView.query.filter_by(material_id=material_id).delete()
                    logger.info("Записи просмотров материала удалены")
                except Exception as e:
                    logger.warning(f"Ошибка при удалении записей просмотров: {str(e)}")

                # Удаление изображений
                if material.image_path:
                    try:
                        image_path = os.path.join(app.static_folder, 'img', 'materials', material.image_path)
                        logger.info(f"Удаляем главное изображение: {image_path}")
                        if os.path.exists(image_path):
                            os.remove(image_path)
                    except Exception as e:
                        logger.warning(f"Ошибка при удалении главного изображения: {e}")

                for image in material.images:
                    try:
                        image_path = os.path.join(app.static_folder, 'img', 'materials', image.image_path)
                        logger.info(f"Удаляем дополнительное изображение: {image_path}")
                        if os.path.exists(image_path):
                            os.remove(image_path)
                    except Exception as e:
                        logger.warning(f"Ошибка при удалении дополнительного изображения: {e}")



                # Удаляем сам материал
                logger.info("Удаляем материал из базы данных")
                db.session.delete(material)
                db.session.commit()
                logger.info("Материал успешно удален")

                # Добавляем флеш-сообщение
                flash('Матеріал було успішно видалено', 'success')
                
                return jsonify({
                    'success': True,
                    'redirect': url_for('brand', brand_id=brand_id),
                    'message': 'Матеріал було успішно видалено'
                })

            except Exception as e:
                db.session.rollback()
                logger.error(f"Ошибка при удалении материала: {str(e)}")
                logger.error(traceback.format_exc())
                return jsonify({
                    'error': 'Помилка при видаленні матеріалу',
                    'details': str(e)
                }), 500

    except Exception as e:
        logger.error(f"Непредвиденная ошибка в delete_material: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': 'Помилка при видаленні матеріалу',
            'details': str(e)
        }), 500
    finally:
        logger.info(f"=== Завершение удаления материала {material_id} ===")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Ви успішно увійшли в систему', 'success')
            return redirect(url_for('index'))
        flash('Невірний логін або пароль', 'error')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы успешно вышли из системы', 'success')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Пользователь с таким именем уже существует', 'error')
            return redirect(url_for('register'))
            
        if User.query.filter_by(email=email).first():
            flash('Пользователь с таким email уже существует', 'error')
            return redirect(url_for('register'))
            
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Регистрация успешна! Теперь вы можете войти', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/ajax_login', methods=['POST'])
def ajax_login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()
    
    if user and user.check_password(password):
        login_user(user)
        return jsonify({'success': True})
    return jsonify({'error': 'Невірний логін або пароль'})

@app.route('/favicon.ico')
def favicon():
    try:
        return send_from_directory(os.path.join(app.static_folder, 'img', 'icons'),
                                 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    except Exception as e:
        logger.warning(f"Favicon not found: {str(e)}")
        return '', 204  # No content response

@app.route('/add_brand', methods=['POST'])
@login_required
def add_brand():
    if request.method == 'POST':
        name = request.form.get('name')
        image = request.files.get('image')
        source = request.form.get('source')
        
        if not name:
            if request.headers.get('Accept') == 'application/json':
                return jsonify({'error': 'Назва бренду обов\'язкова'}), 400
            flash('Назва бренду обов\'язкова', 'error')
            if source == 'admin_brands':
                return redirect(url_for('manage_brands'))
            return redirect(url_for('index'))
        
        # Проверяем, существует ли бренд с таким названием
        existing_brand = Brand.query.filter_by(name=name).first()
        if existing_brand:
            if request.headers.get('Accept') == 'application/json':
                return jsonify({'error': 'Бренд з такою назвою вже існує'}), 400
            flash('Бренд з такою назвою вже існує', 'error')
            if source == 'admin_brands':
                return redirect(url_for('manage_brands'))
            return redirect(url_for('index'))
        
        # Создаем новый бренд
        brand = Brand(name=name)
        
        # Обрабатываем изображение, если оно есть
        if image and image.filename:
            filename = secure_filename(image.filename)
            image_path = os.path.join('img/brands', filename)
            full_path = os.path.join(app.static_folder, 'img/brands', filename)
            
            # Создаем директорию, если её нет
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Сохраняем файл
            image.save(full_path)
            brand.image_path = filename
        
        try:
            db.session.add(brand)
            db.session.commit()
            
            # Устанавливаем flash-сообщение перед отправкой JSON-ответа
            flash('Бренд успішно додано', 'success')
            
            if request.headers.get('Accept') == 'application/json':
                return jsonify({
                    'success': True,
                    'message': 'Бренд успішно додано',
                    'redirect': url_for('index')
                })
            
            # Проверяем откуда пришел запрос и перенаправляем соответственно
            if source == 'admin_brands':
                return redirect(url_for('manage_brands'))
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            if request.headers.get('Accept') == 'application/json':
                return jsonify({'error': 'Помилка при додаванні бренду'}), 500
            flash('Помилка при додаванні бренду', 'error')
            app.logger.error(f'Error adding brand: {str(e)}')
            if source == 'admin_brands':
                return redirect(url_for('manage_brands'))
            return redirect(url_for('index'))

@app.route('/login_modal', methods=['POST'])
def login_modal():
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Будь ласка, заповніть всі поля'})
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return jsonify({'success': True})
        
        return jsonify({'success': False, 'message': 'Невірний логін або пароль'})
    except Exception as e:
        logger.error(f"Error in login_modal: {str(e)}")
        return jsonify({'success': False, 'message': 'Помилка сервера. Спробуйте пізніше'})

@app.route('/create_test/<int:material_id>', methods=['GET', 'POST'])
@login_required
def create_test(material_id):
    logger.info("=== Начало создания теста ===")
    logger.info(f"Material ID: {material_id}")
    
    if current_user.role != 'admin':
        logger.warning(f"Попытка создания теста пользователем без прав админа: {current_user.username}")
        flash('У вас немає прав для створення тестів', 'danger')
        return redirect(url_for('view_material', material_id=material_id))
    
    material = Material.query.get_or_404(material_id)
    logger.info(f"Материал найден: {material.title}")
    
    if request.method == 'POST':
        logger.info("Получен POST запрос")
        logger.info(f"Form data: {request.form}")
        
        questions = request.form.getlist('questions[]')
        correct_answers = request.form.getlist('correct_answers[]')
        wrong_answers_1 = request.form.getlist('wrong_answers_1[]')
        wrong_answers_2 = request.form.getlist('wrong_answers_2[]')
        wrong_answers_3 = request.form.getlist('wrong_answers_3[]')
        
        logger.info(f"Получено вопросов: {len(questions)}")
        logger.info(f"Получено правильных ответов: {len(correct_answers)}")
        logger.info(f"Получено неправильных ответов 1: {len(wrong_answers_1)}")
        logger.info(f"Получено неправильных ответов 2: {len(wrong_answers_2)}")
        logger.info(f"Получено неправильных ответов 3: {len(wrong_answers_3)}")
        
        # Проверка количества вопросов
        if len(questions) < 5:
            logger.warning(f"Недостаточно вопросов: {len(questions)}")
            flash('Тест повинен містити мінімум 5 питань', 'danger')
            return render_template('test_create.html', 
                                material=material,
                                questions_data=questions,
                                correct_answers=correct_answers,
                                wrong_answers_1=wrong_answers_1,
                                wrong_answers_2=wrong_answers_2,
                                wrong_answers_3=wrong_answers_3)
        
        # Проверка на дубликаты вопросов
        question_set = set()
        has_duplicates = False
        for question in questions:
            if question.lower() in question_set:
                has_duplicates = True
                logger.warning(f"Найден дубликат вопроса: {question}")
                break
            question_set.add(question.lower())
        
        if has_duplicates:
            flash('Знайдено дублікати питань. Будь ласка, перевірте червоні поля.', 'danger')
            return render_template('test_create.html', 
                                material=material,
                                questions_data=questions,
                                correct_answers=correct_answers,
                                wrong_answers_1=wrong_answers_1,
                                wrong_answers_2=wrong_answers_2,
                                wrong_answers_3=wrong_answers_3)
        
        # Проверка уникальности ответов для каждого вопроса
        for i in range(len(questions)):
            answers = [correct_answers[i], wrong_answers_1[i], wrong_answers_2[i], wrong_answers_3[i]]
            if len(set(answers)) != len(answers):
                logger.warning(f"Найдены дубликаты ответов в вопросе {i+1}")
                flash('Всі відповіді на одне питання повинні бути унікальними', 'danger')
                return render_template('test_create.html', 
                                    material=material,
                                    questions_data=questions,
                                    correct_answers=correct_answers,
                                    wrong_answers_1=wrong_answers_1,
                                    wrong_answers_2=wrong_answers_2,
                                    wrong_answers_3=wrong_answers_3)
        
        try:
            logger.info("Начало создания теста в базе данных")
            # Создание теста
            test = Test(material_id=material_id)
            db.session.add(test)
            db.session.flush()  # Получаем ID теста
            logger.info(f"Создан тест с ID: {test.id}")
            
            # Создание вопросов
            for i in range(len(questions)):
                logger.info(f"Создание вопроса {i+1}")
                logger.info(f"Текст вопроса: {questions[i]}")
                logger.info(f"Правильный ответ: {correct_answers[i]}")
                
                try:
                    question = TestQuestion(
                        test_id=test.id,
                        text=questions[i],
                        correct_answer=correct_answers[i]
                    )
                    db.session.add(question)
                    db.session.flush()  # Получаем ID вопроса
                    logger.info(f"Создан вопрос с ID: {question.id}")
                    
                    # Создаем ответы для вопроса
                    answers = [
                        TestAnswer(question_id=question.id, text=correct_answers[i]),
                        TestAnswer(question_id=question.id, text=wrong_answers_1[i]),
                        TestAnswer(question_id=question.id, text=wrong_answers_2[i]),
                        TestAnswer(question_id=question.id, text=wrong_answers_3[i])
                    ]
                    for answer in answers:
                        db.session.add(answer)
                        logger.info(f"Добавлен ответ: {answer.text}")
                except Exception as e:
                    logger.error(f"Ошибка при создании вопроса {i+1}: {str(e)}")
                    logger.error(f"Тип ошибки: {type(e)}")
                    logger.error(f"Детали ошибки: {traceback.format_exc()}")
                    raise
            
            db.session.commit()
            logger.info("Тест успешно создан и сохранен в базе данных")
            flash('Тест успішно створено', 'success')
            return redirect(url_for('view_material', material_id=material_id))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Помилка при створенні тесту: {str(e)}")
            logger.error(f"Тип ошибки: {type(e)}")
            logger.error(f"Детали ошибки: {traceback.format_exc()}")
            flash('Помилка при створенні тесту', 'error')
            return render_template('test_create.html', 
                                material=material,
                                questions_data=questions,
                                correct_answers=correct_answers,
                                wrong_answers_1=wrong_answers_1,
                                wrong_answers_2=wrong_answers_2,
                                wrong_answers_3=wrong_answers_3)
    
    return render_template('test_create.html', material=material)

@app.route('/material/<int:material_id>/test')
def take_test(material_id):
    material = Material.query.get_or_404(material_id)
    test = Test.query.filter_by(material_id=material_id).first()
    
    if not test:
        flash('Тест для цього матеріалу ще не створено', 'error')
        return redirect(url_for('view_material', material_id=material_id))
    
    # Получаем все вопросы теста
    all_questions = TestQuestion.query.filter_by(test_id=test.id).all()
    
    # Если вопросов меньше 15, используем все
    # Если больше 15, выбираем случайные 15
    import random
    if len(all_questions) > 15:
        questions = random.sample(all_questions, 15)
    else:
        questions = all_questions
    
    # Перемешиваем порядок вопросов
    random.shuffle(questions)
    
    # Для каждого вопроса перемешиваем ответы
    for question in questions:
        # Получаем все ответы для вопроса
        answers = TestAnswer.query.filter_by(question_id=question.id).all()
        # Перемешиваем ответы
        random.shuffle(answers)
        question.answers = answers
    
    return render_template('test_take.html', 
                         material=material,
                         test=test,
                         questions=questions)

@app.route('/test/<int:test_id>/submit', methods=['POST'])
def submit_test(test_id):
    test = Test.query.get_or_404(test_id)
    material = Material.query.get_or_404(test.material_id)
    
    # Получаем время начала теста из формы
    test_started_at_str = request.form.get('test_started_at')
    started_at = None
    time_taken = None
    
    if test_started_at_str:
        try:
            from datetime import datetime
            # Парсим время начала (ISO формат из JavaScript)
            started_at = datetime.fromisoformat(test_started_at_str.replace('Z', '+00:00'))
            # Вычисляем время прохождения в секундах
            end_time = datetime.now(started_at.tzinfo) if started_at.tzinfo else datetime.utcnow()
            time_taken = int((end_time - started_at).total_seconds())
        except (ValueError, TypeError) as e:
            logger.warning(f"Ошибка при парсинге времени начала теста: {e}")
    
    # Получаем все вопросы теста
    questions = TestQuestion.query.filter_by(test_id=test_id).all()
    
    # Считаем правильные ответы
    correct_answers = 0
    total_questions = len(questions)
    
    # Создаем запись о результатах теста
    test_result = TestResult(
        user_id=current_user.id if current_user.is_authenticated else 1,  # Гостевой аккаунт, если пользователь не авторизован
        test_id=test_id,
        score=0,  # Предварительно, обновим позже
        max_score=total_questions,
        started_at=started_at,
        time_taken=time_taken
    )
    db.session.add(test_result)
    db.session.flush()  # Получаем ID результата
    
    # Сохраняем ответы на вопросы
    for question in questions:
        answer_id = request.form.get(f'question_{question.id}')
        if answer_id:
            answer = TestAnswer.query.get(answer_id)
            is_correct = False
            answer_text = ""
            
            if answer:
                answer_text = answer.text
                is_correct = (answer.text == question.correct_answer)
                if is_correct:
                    correct_answers += 1
            
            # Сохраняем результат ответа на вопрос
            question_result = TestQuestionResult(
                test_result_id=test_result.id,
                question_id=question.id,
                answer_given=answer_text,
                is_correct=is_correct
            )
            db.session.add(question_result)
    
    # Вычисляем процент правильных ответов
    score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    # Обновляем итоговый результат
    test_result.score = round(score)
    
    # Если тест пройден успешно (>= 80%), отмечаем назначение как завершенное
    if current_user.is_authenticated and score >= 80:
        assignment = TestAssignment.query.filter(
            TestAssignment.user_id == current_user.id,
            TestAssignment.material_id == material.id,
            TestAssignment.is_completed == False
        ).first()
        
        if assignment:
            assignment.is_completed = True
    
    db.session.commit()
    
    # Определяем результат
    if score >= 80:
        result = "Відмінно"
    elif score >= 60:
        result = "Добре"
    else:
        result = "Потрібно повторити матеріал"
    
    return render_template('test_result.html',
                         material=material,
                         score=score,
                         correct_answers=correct_answers,
                         total_questions=total_questions,
                         result=result)

@app.route('/material/<int:material_id>/preview_test')
@login_required
def preview_test(material_id):
    if current_user.role != 'admin':
        flash('У вас немає прав для цієї дії', 'error')
        return redirect(url_for('view_material', material_id=material_id))
    
    material = Material.query.get_or_404(material_id)
    questions = TestQuestion.query.filter_by(material_id=material_id).all()
    
    if not questions:
        flash('Тест для цього матеріалу не знайдено', 'error')
        return redirect(url_for('view_material', material_id=material_id))
    
    return render_template('test_preview.html',
                         material=material,
                         questions=questions)

@app.route("/moderate_test/<int:material_id>", methods=["GET", "POST"])
@login_required
def moderate_test(material_id):
    if current_user.role != 'admin':
        flash('У вас немає прав для цієї дії', 'error')
        return redirect(url_for('view_material', material_id=material_id))
    
    try:
        material = Material.query.get_or_404(material_id)
        
        # Получаем немодерированные вопросы
        unmoderated_questions = TestQuestion.query.filter_by(material_id=material_id).all()
        
        if not unmoderated_questions:
            flash('Немає немодерированих тестів для цього матеріалу', 'error')
            return redirect(url_for('view_material', material_id=material_id))
        
        if request.method == "POST":
            try:
                # Удаляем существующие вопросы для этого материала
                TestQuestion.query.filter_by(material_id=material.id).delete()
                
                # Читаем отредактированные вопросы с формы и сохраняем
                for i in range(len(request.form)//6):
                    question = TestQuestion(
                        material_id=material.id,
                        text=request.form[f"q{i}"],
                        correct_answer=request.form[f"c{i}"],
                        wrong_1=request.form[f"w{i}1"],
                        wrong_2=request.form[f"w{i}2"],
                        wrong_3=request.form[f"w{i}3"],
                    )
                    db.session.add(question)
                
                # Удаляем немодерированные вопросы
                TestQuestion.query.filter_by(material_id=material_id).delete()
                
                db.session.commit()
                flash("Тест успішно додано до бази!", "success")
                return redirect(url_for('view_material', material_id=material.id))
                
            except Exception as e:
                db.session.rollback()
                logger.error(f"Помилка при збереженні тесту: {str(e)}")
                flash('Помилка при збереженні тесту', 'error')
                return redirect(url_for('moderate_test', material_id=material_id))
        
        # Для GET запроса отображаем форму модерации
        return render_template("test_moderate.html", 
                             material=material)
                             
    except Exception as e:
        logger.error(f"Unexpected error in moderate_test: {str(e)}")
        flash('Сталася неочікувана помилка', 'error')
        return redirect(url_for('view_material', material_id=material_id))

@app.route('/material/<int:material_id>/edit_test', methods=['GET', 'POST'])
@login_required
def edit_test(material_id):
    if current_user.role != 'admin':
        flash('У вас немає прав для редагування тестів', 'error')
        return redirect(url_for('view_material', material_id=material_id))
    
    material = Material.query.get_or_404(material_id)
    test = Test.query.filter_by(material_id=material_id).first()
    
    if not test:
        flash('Тест не знайдено', 'error')
        return redirect(url_for('view_material', material_id=material_id))
    
    if request.method == 'POST':
        try:
            # Получаем данные из формы
            questions = request.form.getlist('questions[]')
            correct_answers = request.form.getlist('correct_answers[]')
            wrong_answers_1 = request.form.getlist('wrong_answers_1[]')
            wrong_answers_2 = request.form.getlist('wrong_answers_2[]')
            wrong_answers_3 = request.form.getlist('wrong_answers_3[]')
            
            logger.info("=== Данные формы ===")
            logger.info(f"Количество вопросов: {len(questions)}")
            logger.info(f"Количество правильных ответов: {len(correct_answers)}")
            logger.info(f"Количество неправильных ответов 1: {len(wrong_answers_1)}")
            logger.info(f"Количество неправильных ответов 2: {len(wrong_answers_2)}")
            logger.info(f"Количество неправильных ответов 3: {len(wrong_answers_3)}")
            
            # Проверяем, что все массивы имеют одинаковую длину
            if not (len(questions) == len(correct_answers) == len(wrong_answers_1) == len(wrong_answers_2) == len(wrong_answers_3)):
                logger.error("Несоответствие количества вопросов и ответов")
                flash('Количество ответов не соответствует количеству вопросов', 'error')
                return render_template('test_edit.html', 
                                    material=material, 
                                    test=test, 
                                    questions=TestQuestion.query.filter_by(test_id=test.id).all())
            
            # Проверка на дубликаты вопросов
            question_set = set()
            has_duplicates = False
            for question in questions:
                if question.lower() in question_set:
                    has_duplicates = True
                    logger.warning(f"Найден дубликат вопроса: {question}")
                    break
                question_set.add(question.lower())
            
            if has_duplicates:
                flash('Знайдено дублікати питань. Будь ласка, перевірте червоні поля.', 'error')
                return render_template('test_edit.html', 
                                    material=material, 
                                    test=test, 
                                    questions=TestQuestion.query.filter_by(test_id=test.id).all())
            
            # Проверка уникальности ответов для каждого вопроса
            for i in range(len(questions)):
                answers = [correct_answers[i], wrong_answers_1[i], wrong_answers_2[i], wrong_answers_3[i]]
                if len(set(answers)) != len(answers):
                    logger.warning(f"Найдены дубликаты ответов в вопросе {i+1}")
                    flash('Всі відповіді на одне питання повинні бути унікальними', 'error')
                    return render_template('test_edit.html', 
                                        material=material, 
                                        test=test, 
                                        questions=TestQuestion.query.filter_by(test_id=test.id).all())
            
            # Получаем все существующие вопросы теста
            existing_questions = TestQuestion.query.filter_by(test_id=test.id).all()
            
            # Сначала удаляем все ответы для существующих вопросов
            for question in existing_questions:
                TestAnswer.query.filter_by(question_id=question.id).delete()
            
            # Затем удаляем сами вопросы
            TestQuestion.query.filter_by(test_id=test.id).delete()
            db.session.flush()
            
            # Создаем новые вопросы и ответы
            for i in range(len(questions)):
                question = TestQuestion(
                    test_id=test.id,
                    text=questions[i],
                    correct_answer=correct_answers[i]
                )
                db.session.add(question)
                db.session.flush()  # Получаем ID вопроса
                
                # Создаем ответы для вопроса
                answers = [
                    TestAnswer(question_id=question.id, text=correct_answers[i]),
                    TestAnswer(question_id=question.id, text=wrong_answers_1[i]),
                    TestAnswer(question_id=question.id, text=wrong_answers_2[i]),
                    TestAnswer(question_id=question.id, text=wrong_answers_3[i])
                ]
                for answer in answers:
                    db.session.add(answer)
            
            db.session.commit()
            flash('Тест успішно оновлено', 'success')
            return redirect(url_for('view_material', material_id=material_id))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Ошибка при обновлении теста: {str(e)}")
            logger.error(f"Тип ошибки: {type(e)}")
            logger.error(f"Детали ошибки: {traceback.format_exc()}")
            flash('Сталася помилка при оновленні тесту', 'error')
            return render_template('test_edit.html', 
                                material=material, 
                                test=test, 
                                questions=TestQuestion.query.filter_by(test_id=test.id).all())
    
    # Для GET запроса получаем существующие вопросы и ответы
    questions = TestQuestion.query.filter_by(test_id=test.id).all()
    return render_template('test_edit.html', material=material, test=test, questions=questions)

@app.route('/clear_questions', methods=['GET'])
@login_required
def clear_questions():
    if current_user.role != 'admin':
        flash('У вас немає прав для цієї дії', 'error')
        return redirect(url_for('index'))
    
    try:
        # Сначала удаляем все ответы
        TestAnswer.query.delete()
        # Затем удаляем все вопросы
        TestQuestion.query.delete()
        # И наконец удаляем все тесты
        Test.query.delete()
        
        db.session.commit()
        flash('Всі питання успішно видалено', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Помилка при видаленні питань: {str(e)}")
        flash('Помилка при видаленні питань', 'error')
    
    return redirect(url_for('index'))

@app.route('/user/profile', defaults={'user_id': None})
@app.route('/user/profile/<int:user_id>')
@login_required
def user_profile(user_id):
    if current_user.role == 'admin' and user_id:
        user = User.query.get_or_404(user_id)
    else:
        user = current_user

    # Получаем результаты тестов пользователя
    test_results = TestResult.query.filter_by(user_id=user.id).order_by(TestResult.created_at.desc()).all()
    
    # Рассчитываем статистику
    total_tests = len(test_results)
    passed_tests = sum(1 for r in test_results if r.score >= 80)
    failed_tests = total_tests - passed_tests
    avg_score = sum(r.score for r in test_results) / total_tests if total_tests > 0 else 0
    
    # Находим руководителя отдела пользователя
    department_head = None
    if user.department:
        department_head = User.query.filter_by(
            department=user.department,
            position='department_head'
        ).first()
    
    # Получаем назначенные тесты пользователя
    from datetime import datetime, timedelta
    assigned_tests = TestAssignment.query.filter_by(user_id=user.id).order_by(TestAssignment.created_at.desc()).all()
    
    # Добавляем информацию о днях до окончания срока для каждого назначенного теста
    for assignment in assigned_tests:
        now = datetime.utcnow()
        if assignment.end_date > now:
            days_left = (assignment.end_date - now).days
            assignment.days_left = days_left
        else:
            assignment.days_left = 0
    
    return render_template('user_profile.html', 
                        user=user,
                        test_results=test_results,
                        total_tests=total_tests,
                        passed_tests=passed_tests,
                        failed_tests=failed_tests,
                        avg_score=round(avg_score, 1),
                        department_head=department_head,
                        assigned_tests=assigned_tests)

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    try:
        if current_user.role != 'admin':
            flash('У вас нет прав для доступа к этой странице', 'error')
            return redirect(url_for('index'))
        
        # Получаем всех пользователей
        users = User.query.all()
        
        # Получаем все результаты тестов
        test_results = TestResult.query.order_by(TestResult.created_at.desc()).all()
        
        # Общая статистика
        total_attempts = len(test_results)
        avg_score = sum(r.score for r in test_results) / total_attempts if total_attempts > 0 else 0
        passed_tests = sum(1 for r in test_results if r.score >= 80)
        success_rate = (passed_tests / total_attempts * 100) if total_attempts > 0 else 0
        
        # Статистика по брендам для графика "Найкраще знають"
        brands_stats = {}
        
        # Получаем все бренды
        all_brands = Brand.query.all()
        for brand in all_brands:
            brands_stats[brand.id] = {
                'brand': brand,
                'scores': [],
                'avg_score': 0,
                'tests_count': 0
            }
        
        # Собираем результаты по брендам
        for result in test_results:
            test = Test.query.get(result.test_id)
            if test:
                material = Material.query.get(test.material_id)
                if material and material.brand_id in brands_stats:
                    brands_stats[material.brand_id]['scores'].append(result.score)
                    brands_stats[material.brand_id]['tests_count'] += 1
        
        # Рассчитываем средние баллы для брендов
        for brand_id in brands_stats:
            scores = brands_stats[brand_id]['scores']
            if scores:
                brands_stats[brand_id]['avg_score'] = sum(scores) / len(scores)
        
        # Формируем данные для графика, сортируем по убыванию среднего балла
        chart_data = []
        for brand_id, data in brands_stats.items():
            if data['tests_count'] > 0:  # Только бренды с тестами
                chart_data.append({
                    'label': data['brand'].name,
                    'value': round(data['avg_score'], 1),
                    'tests_count': data['tests_count']
                })
        
        chart_data.sort(key=lambda x: x['value'], reverse=True)
        
        # Проблемные тесты (с низким средним баллом)
        tests_stats = {}
        for result in test_results:
            test_id = result.test_id
            if test_id not in tests_stats:
                test = Test.query.get(test_id)
                if test:
                    tests_stats[test_id] = {
                        'test': test,
                        'scores': [],
                        'times': [],  # Добавляем список времени
                        'avg_score': 0,
                        'attempts_count': 0,
                        'total_time': 0,
                        'avg_time': 0,
                        'avg_time_formatted': 'N/A'
                    }
            
            if test_id in tests_stats:
                tests_stats[test_id]['scores'].append(result.score)
                tests_stats[test_id]['attempts_count'] += 1
                
                # Добавляем время если оно есть (время в секундах из базы)
                if result.time_taken:
                    tests_stats[test_id]['times'].append(result.time_taken)
                    tests_stats[test_id]['total_time'] += result.time_taken
        
        # Рассчитываем статистику для каждого теста
        for test_id in tests_stats:
            scores = tests_stats[test_id]['scores']
            times = tests_stats[test_id]['times']
            
            # Средний балл
            tests_stats[test_id]['avg_score'] = sum(scores) / len(scores) if scores else 0
            
            # Среднее время
            if times:
                avg_time_seconds = sum(times) / len(times)
                tests_stats[test_id]['avg_time'] = avg_time_seconds
                
                # Форматируем среднее время
                minutes = int(avg_time_seconds // 60)
                seconds = int(avg_time_seconds % 60)
                if minutes > 0:
                    tests_stats[test_id]['avg_time_formatted'] = f"{minutes}хв {seconds}с"
                else:
                    tests_stats[test_id]['avg_time_formatted'] = f"{seconds}с"
            else:
                tests_stats[test_id]['avg_time_formatted'] = '-'
            
            # Форматируем общее время
            total_minutes = tests_stats[test_id]['total_time'] // 60
            total_seconds = tests_stats[test_id]['total_time'] % 60
            if total_minutes > 60:
                hours = total_minutes // 60
                remaining_minutes = total_minutes % 60
                tests_stats[test_id]['total_time_formatted'] = f"{hours}год {remaining_minutes}хв"
            elif total_minutes > 0:
                tests_stats[test_id]['total_time_formatted'] = f"{total_minutes}хв {total_seconds}с"
            else:
                tests_stats[test_id]['total_time_formatted'] = f"{total_seconds}с" if tests_stats[test_id]['total_time'] > 0 else "-"
        
        # Сортируем тесты по среднему баллу (по возрастанию)
        problematic_tests = sorted(
            [{
                'test': data['test'], 
                'avg_score': data['avg_score'],
                'attempts_count': data['attempts_count'],
                'total_time_formatted': data['total_time_formatted'],
                'avg_time_formatted': data['avg_time_formatted']
            } for test_id, data in tests_stats.items()],
            key=lambda x: x['avg_score']
        )[:5]  # Топ-5 проблемных тестов
        
        # Проблемные пользователи (с низким средним баллом)
        users_stats = {}
        for result in test_results:
            user_id = result.user_id
            if user_id not in users_stats:
                user = User.query.get(user_id)
                if user:
                    users_stats[user_id] = {
                        'user': user,
                        'scores': [],
                        'times': [],  # Добавляем список времени
                        'avg_score': 0,
                        'tests_count': 0,
                        'total_time': 0,
                        'avg_time': 0,
                        'avg_time_formatted': 'N/A'
                    }
            
            if user_id in users_stats:
                users_stats[user_id]['scores'].append(result.score)
                users_stats[user_id]['tests_count'] += 1
                
                # Добавляем время если оно есть (время в секундах из базы)
                if result.time_taken:
                    users_stats[user_id]['times'].append(result.time_taken)
                    users_stats[user_id]['total_time'] += result.time_taken
        
        # Рассчитываем статистику для каждого пользователя
        for user_id in users_stats:
            scores = users_stats[user_id]['scores']
            times = users_stats[user_id]['times']
            
            # Средний балл
            users_stats[user_id]['avg_score'] = sum(scores) / len(scores) if scores else 0
            
            # Среднее время
            if times:
                avg_time_seconds = sum(times) / len(times)
                users_stats[user_id]['avg_time'] = avg_time_seconds
                
                # Форматируем среднее время
                minutes = int(avg_time_seconds // 60)
                seconds = int(avg_time_seconds % 60)
                if minutes > 0:
                    users_stats[user_id]['avg_time_formatted'] = f"{minutes}хв {seconds}с"
                else:
                    users_stats[user_id]['avg_time_formatted'] = f"{seconds}с"
            else:
                users_stats[user_id]['avg_time_formatted'] = '-'
            
            # Форматируем общее время
            total_minutes = users_stats[user_id]['total_time'] // 60
            total_seconds = users_stats[user_id]['total_time'] % 60
            if total_minutes > 60:
                hours = total_minutes // 60
                remaining_minutes = total_minutes % 60
                users_stats[user_id]['total_time_formatted'] = f"{hours}год {remaining_minutes}хв"
            elif total_minutes > 0:
                users_stats[user_id]['total_time_formatted'] = f"{total_minutes}хв {total_seconds}с"
            else:
                users_stats[user_id]['total_time_formatted'] = f"{total_seconds}с" if users_stats[user_id]['total_time'] > 0 else "-"
        
        # Сортируем пользователей по среднему баллу (по возрастанию)
        problematic_users = sorted(
            [{
                'user': data['user'], 
                'avg_score': data['avg_score'],
                'tests_count': data['tests_count'],
                'total_time_formatted': data['total_time_formatted'],
                'avg_time_formatted': data['avg_time_formatted']
            } for user_id, data in users_stats.items()],
            key=lambda x: x['avg_score']
        )[:5]  # Топ-5 проблемных пользователей
        
        # Подготавливаем данные для основной таблицы пользователей с полной статистикой
        users_with_stats = []
        for user in users:
            if user.id in users_stats:
                user_data = users_stats[user.id]
                users_with_stats.append({
                    'id': user.id,
                    'username': user.username,
                    'tests_count': user_data['tests_count'],
                    'avg_score': user_data['avg_score'],
                    'total_time_formatted': user_data['total_time_formatted'],
                    'avg_time_formatted': user_data['avg_time_formatted'],
                    'total_time_seconds': user_data['total_time'],
                    'avg_time_seconds': user_data['avg_time']
                })
            else:
                # Пользователь без результатов тестов
                users_with_stats.append({
                    'id': user.id,
                    'username': user.username,
                    'tests_count': 0,
                    'avg_score': 0,
                    'total_time_formatted': '-',
                    'avg_time_formatted': '-',
                    'total_time_seconds': 0,
                    'avg_time_seconds': 0
                })
        
        return render_template('admin_dashboard.html',
                             users=users,
                             users_with_stats=users_with_stats,
                             total_attempts=total_attempts,
                             avg_score=round(avg_score, 1),
                             success_rate=round(success_rate, 1),
                             chart_data=chart_data,
                             problematic_tests=problematic_tests,
                             problematic_users=problematic_users)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in admin_dashboard: {str(e)}")
        flash('Сталася помилка при завантаженні панелі адміністратора', 'error')
        return redirect(url_for('index'))

@app.route('/api/admin/user_tests/<int:user_id>')
@login_required
def api_user_tests(user_id):
    try:
        if current_user.role != 'admin':
            return jsonify({'error': 'Недостаточно прав'}), 403
        
        user = User.query.get_or_404(user_id)
        logger.info(f"Getting test results for user {user.username}")
        
        # Получаем результаты тестов пользователя, сгруппированные по бренду
        brands_data = {}
        
        # Получаем все результаты тестов пользователя
        user_results = TestResult.query.filter_by(user_id=user_id).all()
        logger.info(f"Found {len(user_results)} test results for user")
        
        for result in user_results:
            test = Test.query.get(result.test_id)
            if not test:
                logger.warning(f"Test {result.test_id} not found")
                continue
                
            material = Material.query.get(test.material_id)
            if not material:
                logger.warning(f"Material for test {test.id} not found")
                continue
                
            brand = Brand.query.get(material.brand_id)
            if not brand:
                logger.warning(f"Brand for material {material.id} not found")
                continue
            
            logger.info(f"Processing result for brand: {brand.name}, material: {material.title}")
            
            # Добавляем бренд, если его еще нет
            if brand.id not in brands_data:
                brands_data[brand.id] = {
                    'id': brand.id,
                    'name': brand.name,
                    'materials': {}
                }
            
            # Добавляем материал, если его еще нет
            if material.id not in brands_data[brand.id]['materials']:
                brands_data[brand.id]['materials'][material.id] = {
                    'id': material.id,
                    'title': material.title,
                    'attempts': []
                }
            
            # Добавляем информацию о прохождении теста
            correct_answers = int(result.score * result.max_score / 100)
            wrong_answers = result.max_score - correct_answers
            
            # Получаем детальную информацию по ответам на вопросы
            question_details = []
            test_question_results = TestQuestionResult.query.filter_by(test_result_id=result.id).all()
            
            for question_result in test_question_results:
                question = TestQuestion.query.get(question_result.question_id)
                if question:
                    question_details.append({
                        'question_text': question.text,
                        'user_answer': question_result.answer_given,
                        'correct_answer': question.correct_answer,
                        'is_correct': question_result.is_correct
                    })
            
            attempt_data = {
                'id': result.id,
                'date': result.created_at.strftime('%d.%m.%Y %H:%M'),
                'score': result.score,
                'correct_answers': correct_answers,
                'wrong_answers': wrong_answers,
                'time_taken': result.time_taken_formatted,  # Используем отформатированное время
                'question_details': question_details
            }
            
            brands_data[brand.id]['materials'][material.id]['attempts'].append(attempt_data)
            logger.info(f"Added attempt with score {result.score}% to material {material.title}")
        
        # Преобразуем словари в списки для удобства использования в шаблоне
        brands_list = []
        for brand_id, brand_data in brands_data.items():
            materials_list = []
            brand_total_attempts = 0
            brand_total_score = 0
            brand_total_time_seconds = 0
            brand_attempts_with_time = 0
            
            for material_id, material_data in brand_data['materials'].items():
                materials_list.append({
                    'id': material_id,
                    'title': material_data['title'],
                    'attempts': material_data['attempts']
                })
                
                # Считаем статистику по бренду
                for attempt in material_data['attempts']:
                    brand_total_attempts += 1
                    brand_total_score += attempt['score']
                    
                    # Добавляем время если оно есть (время в секундах из базы)
                    if attempt.get('time_taken') and attempt['time_taken'] != '-':
                        # Находим соответствующий результат для получения времени в секундах
                        result = TestResult.query.get(attempt['id'])
                        if result and result.time_taken:
                            brand_total_time_seconds += result.time_taken
                            brand_attempts_with_time += 1
            
            # Рассчитываем средние значения
            brand_avg_score = brand_total_score / brand_total_attempts if brand_total_attempts > 0 else 0
            brand_avg_time_seconds = brand_total_time_seconds / brand_attempts_with_time if brand_attempts_with_time > 0 else 0
            
            # Форматируем время
            def format_time(seconds):
                if seconds == 0:
                    return '-'
                minutes = int(seconds // 60)
                secs = int(seconds % 60)
                if minutes > 0:
                    return f"{minutes}хв {secs}с"
                else:
                    return f"{secs}с"
            
            # Форматируем общее время
            total_minutes = brand_total_time_seconds // 60
            total_seconds = brand_total_time_seconds % 60
            if total_minutes > 60:
                hours = total_minutes // 60
                remaining_minutes = total_minutes % 60
                brand_total_time_formatted = f"{hours}год {remaining_minutes}хв"
            elif total_minutes > 0:
                brand_total_time_formatted = f"{total_minutes}хв {total_seconds}с"
            else:
                brand_total_time_formatted = f"{total_seconds}с" if brand_total_time_seconds > 0 else "-"
            
            brands_list.append({
                'id': brand_id,
                'name': brand_data['name'],
                'materials': materials_list,
                'stats': {
                    'tests_count': brand_total_attempts,
                    'avg_score': round(brand_avg_score, 1),
                    'total_time_formatted': brand_total_time_formatted,
                    'avg_time_formatted': format_time(brand_avg_time_seconds)
                }
            })
        
        response_data = {
            'user': {
                'id': user.id,
                'username': user.username
            },
            'brands': brands_list
        }
        
        logger.info(f"Final response structure: {response_data}")
        return jsonify(response_data)
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in api_user_tests: {str(e)}")
        logger.error(f"Error details: {traceback.format_exc()}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    try:
        return send_from_directory(app.static_folder, filename)
    except Exception as e:
        logger.warning(f"Static file not found: {filename}, error: {str(e)}")
        return '', 204  # No content response

@app.errorhandler(Exception)
def handle_error(error):
    logger.error(f"Сталася помилка: {str(error)}")
    logger.error(traceback.format_exc())
    
    # Если запрос ожидает JSON, возвращаем JSON-ответ
    if request.is_json or request.headers.get('Accept') == 'application/json':
        return jsonify({
            'error': 'Внутрішня помилка сервера',
            'details': str(error)
        }), 500
    
    # Иначе возвращаем HTML-страницу с ошибкой
    return render_template('error.html', error=error), 500

@app.route('/admin/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        flash('У вас нет прав для доступа к этой странице', 'error')
        return redirect(url_for('index'))
    
    form = AddUserForm()
    if form.validate_on_submit():
        try:
            # Check if user already exists
            if User.query.filter_by(username=form.username.data).first():
                flash('Користувач з таким ім\'ям вже існує', 'error')
                return render_template('admin/users.html', form=form, users=User.query.all())
            
            # Handle photo upload
            photo_filename = None
            if form.photo.data:
                photo = form.photo.data
                if photo.filename:
                    # Create user photos directory if it doesn't exist
                    photos_dir = os.path.join(app.static_folder, 'img', 'users')
                    os.makedirs(photos_dir, exist_ok=True)
                    
                    # Generate secure filename
                    filename = secure_filename(photo.filename)
                    # Add timestamp to prevent conflicts
                    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_')
                    photo_filename = timestamp + filename
                    
                    # Save photo
                    photo_path = os.path.join(photos_dir, photo_filename)
                    photo.save(photo_path)
            
            # Create new user
            user = User(
                username=form.username.data,
                role=form.role.data,
                phone_number=form.phone_number.data,
                department=form.department.data,
                position=form.position.data,
                photo_path=photo_filename
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Користувача успішно додано', 'success')
            return redirect(url_for('users'))
            
        except Exception as e:
            db.session.rollback()
            flash('Помилка при створенні користувача', 'error')
            logger.error(f"Error creating user: {str(e)}")
    
    return render_template('admin/users.html', form=form, users=User.query.all())

@app.route('/material/image/<int:image_id>/delete', methods=['POST'])
@login_required
def delete_material_image(image_id):
    image = MaterialImage.query.get_or_404(image_id)
    material = Material.query.get_or_404(image.material_id)
    
    # Проверяем права доступа
    if current_user.role != 'admin':
        flash('У вас нет прав для удаления изображений', 'danger')
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        # Удаляем файл изображения
        if image.image_path:
            image_path = os.path.join(current_app.static_folder, 'img/materials', image.image_path)
            if os.path.exists(image_path):
                os.remove(image_path)
        
        # Удаляем запись из базы данных
        db.session.delete(image)
        db.session.commit()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/admin/test_assignments', methods=['GET', 'POST'])
@login_required
@admin_required
def test_assignments():
    form = TestAssignmentForm()
    
    # Группируем пользователей по отделам
    users_by_department = {}
    
    # Словарь перевода отделов
    department_names = {
        'founders': 'Засновники компанії',
        'general_director': 'Директор',
        'accounting': 'Відділ Бухгалтерії',
        'marketing': 'Відділ Маркетингу',
        'online_sales': 'Відділ Онлайн продажу',
        'offline_sales': 'Відділ Офлайн продажу',
        'foreign_trade': 'Відділ ЗЕД',
        'warehouse': 'Складський відділ',
        'analytics': 'Відділ аналітики',
        'other': 'Інше',
        'abrams_production': 'Виробництво Abrams'
    }
    
    # Словарь перевода должностей
    position_names = {
        'founder': 'Засновник',
        'general_director': 'Директор',
        'accountant': 'Бухгалтер',
        'chief_accountant': 'Головний бухгалтер',
        'department_head': 'Начальник відділу',
        'marketer': 'Маркетолог',
        'marketing_manager': 'Маркетинг менеджер',
        'sales_manager': 'Менеджер з продажу',
        'online_sales_manager': 'Менеджер онлайн продажу',
        'offline_sales_manager': 'Менеджер офлайн продажу',
        'sales_representative': 'Торговий представник',
        'foreign_trade_manager': 'Менеджер ЗЕД',
        'warehouse_manager': 'Завідувач складу',
        'warehouse_worker': 'Складський працівник',
        'analyst': 'Аналітик',
        'data_analyst': 'Аналітик даних',
        'content_manager': 'Контент менеджер',
        'administrator': 'Адміністратор',
        'other': 'Інше'
    }
    
    users = User.query.order_by(User.department, User.username).all()
    for user in users:
        dept_key = user.department or 'other'
        if dept_key not in users_by_department:
            users_by_department[dept_key] = {
                'name': department_names.get(dept_key, dept_key),
                'users': []
            }
        
        # Добавляем переведенную должность к объекту пользователя
        user.position_ua = position_names.get(user.position, user.position) if user.position else None
        users_by_department[dept_key]['users'].append(user)
    
    if request.method == 'POST' and form.validate_on_submit():
        try:
            # Получаем выбранных пользователей
            selected_user_ids = request.form.getlist('user_ids')
            
            if not selected_user_ids:
                flash('Будь ласка, оберіть хоча б одного співробітника', 'error')
                return redirect(url_for('test_assignments'))
            
            # Проверяем, что дата окончания позже даты начала
            if form.end_date.data <= form.start_date.data:
                flash('Дата закінчення повинна бути пізніше дати початку', 'error')
                return redirect(url_for('test_assignments'))
            
            # Проверяем, что у материала есть тест
            material = Material.query.get(form.material_id.data)
            if not Test.query.filter_by(material_id=material.id).first():
                flash('Для цього матеріалу ще не створено тест', 'error')
                return redirect(url_for('test_assignments'))
            
            # Создаем назначения для каждого выбранного пользователя
            created_count = 0
            skipped_count = 0
            
            for user_id in selected_user_ids:
                user_id = int(user_id)
                
                # Проверяем, нет ли уже активного назначения для этого пользователя и материала
                existing_assignment = TestAssignment.query.filter(
                    TestAssignment.user_id == user_id,
                    TestAssignment.material_id == form.material_id.data,
                    TestAssignment.is_completed == False
                ).first()
                
                if existing_assignment:
                    skipped_count += 1
                    continue
                
                # Создаем новое назначение
                assignment = TestAssignment(
                    user_id=user_id,
                    material_id=form.material_id.data,
                    start_date=form.start_date.data,
                    end_date=form.end_date.data,
                    created_by=current_user.id
                )
                
                db.session.add(assignment)
                created_count += 1
            
            db.session.commit()
            
            if created_count > 0:
                flash(f'Тест успішно призначено {created_count} співробітникам', 'success')
                if skipped_count > 0:
                    flash(f'{skipped_count} співробітників вже мають активне призначення цього тесту', 'warning')
            else:
                flash('Усі обрані співробітники вже мають активне призначення цього тесту', 'warning')
            
            return redirect(url_for('test_assignments'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating test assignments: {str(e)}")
            flash('Сталася помилка при призначенні тестів', 'error')

    assignments = TestAssignment.query.order_by(TestAssignment.created_at.desc()).all()
    return render_template('test_assignments.html', 
                         form=form, 
                         assignments=assignments,
                         users_by_department=users_by_department,
                         now=datetime.utcnow())

@app.route('/admin/test_assignments/<int:assignment_id>/delete', methods=['POST'])
@login_required
def delete_test_assignment(assignment_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        assignment = TestAssignment.query.get_or_404(assignment_id)
        db.session.delete(assignment)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/admin/test_assignments/<int:assignment_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_test_assignment(assignment_id):
    assignment = TestAssignment.query.get_or_404(assignment_id)
    form = EditTestAssignmentForm()
    
    if form.validate_on_submit():
        try:
            # Проверяем, что дата окончания позже даты начала
            if form.end_date.data <= form.start_date.data:
                flash('Дата закінчення повинна бути пізніше дати початку', 'error')
                return redirect(url_for('edit_test_assignment', assignment_id=assignment_id))
            
            # Обновляем даты
            assignment.start_date = form.start_date.data
            assignment.end_date = form.end_date.data
            
            db.session.commit()
            flash('Дати успішно оновлено', 'success')
            return redirect(url_for('test_assignments'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating test assignment: {str(e)}")
            flash('Сталася помилка при оновленні дат', 'error')
    
    # Для GET запроса заполняем форму текущими значениями
    if request.method == 'GET':
        form.start_date.data = assignment.start_date
        form.end_date.data = assignment.end_date
    
    return render_template('edit_test_assignment.html', 
                         form=form, 
                         assignment=assignment)

@app.route('/my_assignments')
@login_required
def my_assignments():
    # Получаем все назначения для текущего пользователя
    assignments = TestAssignment.query.filter_by(user_id=current_user.id).all()
    
    # Разделяем на активные и завершенные
    active_assignments = []
    completed_assignments = []
    now = datetime.utcnow()  # Используем UTC время
    
    for assignment in assignments:
        if assignment.end_date > now:
            active_assignments.append(assignment)
        else:
            completed_assignments.append(assignment)
    
    return render_template('my_assignments.html', 
                         assignments=active_assignments,
                         completed_assignments=completed_assignments,
                         now=now)

@app.before_request
def before_request():
    try:
        # Проверяем состояние сессии
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
    except Exception as e:
        db.session.rollback()
        logger.error(f"Database session error: {str(e)}")

@app.after_request
def after_request(response):
    try:
        if response.status_code >= 400:
            db.session.rollback()
        else:
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in after_request: {str(e)}")
    
    # Добавляем заголовки безопасности
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Только для HTTPS в продакшене
    if not app.debug:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    # CSP заголовок для дополнительной защиты от XSS  
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
        "img-src 'self' data: https: blob:; "
        "font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com; "
        "connect-src 'self'; "
        "media-src 'self'; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self';"
    )
    # Временно отключаем CSP для отладки стилей
    # if app.debug:
    #     response.headers['Content-Security-Policy-Report-Only'] = csp
    # else:
    #     response.headers['Content-Security-Policy'] = csp
    
    return response

@app.teardown_appcontext
def shutdown_session(exception=None):
    try:
        if exception:
            db.session.rollback()
        db.session.remove()
    except Exception as e:
        logger.error(f"Error in shutdown_session: {str(e)}")

@app.errorhandler(404)
def not_found_error(error):
    if request.is_json:
        return jsonify({'error': 'Ресурс не знайдено'}), 404
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    if request.is_json:
        return jsonify({'error': 'Внутрішня помилка сервера'}), 500
    return render_template('500.html'), 500

@app.route('/admin/users')
@login_required
@admin_required
def users():
    users = User.query.all()
    form = AddUserForm()
    return render_template('admin/users.html', users=users, form=form)

@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    logger.info(f"=== Начало удаления пользователя {user_id} ===")
    try:
        # Проверяем CSRF-токен
        data = request.get_json()
        if not data or 'csrf_token' not in data:
            logger.error("CSRF token missing")
            return jsonify({'error': 'CSRF token missing'}), 400

        try:
            validate_csrf(data['csrf_token'])
        except Exception as e:
            logger.error(f"CSRF validation error: {str(e)}")
            return jsonify({'error': 'Invalid CSRF token'}), 400

        user = User.query.get_or_404(user_id)
        logger.info(f"Найден пользователь: {user.username}")
        
        # Проверяем, не пытаемся ли удалить последнего администратора
        if user.role == 'admin':
            admin_count = User.query.filter_by(role='admin').count()
            if admin_count <= 1:
                logger.warning(f"Попытка удалить последнего администратора: {user.username}")
                return jsonify({'error': 'Неможливо видалити останнього адміністратора'}), 400
        
        # Проверяем, не пытаемся ли удалить самого себя
        if user.id == current_user.id:
            logger.warning(f"Попытка удалить свой аккаунт: {user.username}")
            return jsonify({'error': 'Неможливо видалити власний обліковий запис'}), 400
        
        try:
            # 1. Удаляем все результаты тестов пользователя и связанные результаты вопросов
            test_results = TestResult.query.filter_by(user_id=user.id).all()
            logger.info(f"Найдено результатов тестов: {len(test_results)}")
            for test_result in test_results:
                TestQuestionResult.query.filter_by(test_result_id=test_result.id).delete()
                logger.info(f"Удалены результаты вопросов для теста {test_result.id}")
            TestResult.query.filter_by(user_id=user.id).delete()
            logger.info("Удалены все результаты тестов пользователя")

            # 2. Удаляем все назначения тестов пользователя (где он назначен)
            TestAssignment.query.filter_by(user_id=user.id).delete()
            logger.info("Удалены все назначения тестов пользователя")

            # 2.1. Удаляем все назначения, которые этот пользователь создавал
            TestAssignment.query.filter_by(created_by=user.id).delete()
            logger.info("Удалены все назначения, созданные пользователем")

            # 3. Удаляем самого пользователя
            db.session.delete(user)
            db.session.commit()
            logger.info(f"Пользователь {user.username} успешно удален")
            
            flash('Користувача успішно видалено', 'success')
            return jsonify({
                'success': True,
                'redirect': url_for('users'),
                'message': 'Користувача успішно видалено'
            })
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Ошибка при удалении данных пользователя: {str(e)}")
            logger.error(f"Детали ошибки: {traceback.format_exc()}")
            return jsonify({'error': 'Помилка при видаленні даних користувача'}), 500
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"Непредвиденная ошибка при удалении пользователя: {str(e)}")
        logger.error(f"Детали ошибки: {traceback.format_exc()}")
        return jsonify({'error': 'Помилка при видаленні користувача'}), 500
    finally:
        logger.info(f"=== Завершение удаления пользователя {user_id} ===")

@app.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = EditUserForm(original_username=user.username)
    
    if request.method == 'GET':
        # Заполняем форму данными пользователя
        form.username.data = user.username
        form.phone_number.data = user.phone_number
        form.role.data = user.role
        form.department.data = user.department
        form.position.data = user.position
    
    if request.method == 'POST' and form.validate_on_submit():
        try:
            # Обновляем основные данные
            user.username = form.username.data
            user.phone_number = form.phone_number.data
            user.role = form.role.data
            user.department = form.department.data
            user.position = form.position.data
            
            # Обновляем пароль только если он был введен
            if form.password.data:
                user.set_password(form.password.data)
                logger.info(f"Password updated for user {user.username}")
            
            # Обрабатываем загрузку фотографии
            if form.photo.data:
                photo = form.photo.data
                if photo.filename:
                    # Создаем папку для фотографий пользователей если её нет
                    photos_dir = os.path.join(app.static_folder, 'img', 'users')
                    os.makedirs(photos_dir, exist_ok=True)
                    
                    # Удаляем старую фотографию если она есть
                    if user.photo_path:
                        old_photo_path = os.path.join(photos_dir, user.photo_path)
                        if os.path.exists(old_photo_path):
                            try:
                                os.remove(old_photo_path)
                                logger.info(f"Removed old photo: {old_photo_path}")
                            except Exception as e:
                                logger.warning(f"Could not remove old photo: {e}")
                    
                    # Генерируем безопасное имя файла
                    filename = secure_filename(photo.filename)
                    # Добавляем временную метку для предотвращения конфликтов
                    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_')
                    photo_filename = timestamp + filename
                    
                    # Сохраняем новую фотографию
                    photo_path = os.path.join(photos_dir, photo_filename)
                    photo.save(photo_path)
                    user.photo_path = photo_filename
                    logger.info(f"New photo saved: {photo_filename}")
            
            # Если пользователь больше не на руководящей должности, удаляем фото
            if not user.requires_photo and user.photo_path:
                photos_dir = os.path.join(app.static_folder, 'img', 'users')
                old_photo_path = os.path.join(photos_dir, user.photo_path)
                if os.path.exists(old_photo_path):
                    try:
                        os.remove(old_photo_path)
                        logger.info(f"Removed photo for non-leadership position: {old_photo_path}")
                    except Exception as e:
                        logger.warning(f"Could not remove photo: {e}")
                user.photo_path = None
            
            db.session.commit()
            flash('Користувача успішно оновлено', 'success')
            return redirect(url_for('users'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating user: {str(e)}")
            flash('Помилка при оновленні користувача', 'error')
    
    return render_template('admin/edit_user.html', form=form, user=user)

@app.route('/admin/users/<int:user_id>/dependencies', methods=['GET'])
@login_required
@admin_required
def check_user_dependencies(user_id):
    try:
        user = User.query.get_or_404(user_id)
        
        # Проверяем результаты тестов
        test_results_count = TestResult.query.filter_by(user_id=user.id).count()
        
        # Проверяем назначенные тесты
        test_assignments_count = TestAssignment.query.filter_by(user_id=user.id).count()
        
        has_dependencies = test_results_count > 0 or test_assignments_count > 0
        
        return jsonify({
            'success': True,
            'has_dependencies': has_dependencies,
            'test_results_count': test_results_count,
            'test_assignments_count': test_assignments_count
        })
        
    except Exception as e:
        logger.error(f"Error checking user dependencies: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Помилка при перевірці залежностей'
        }), 500

def get_or_create_default_category():
    """Получить или создать категорию 'Без категарії'"""
    from models import Category
    default_category = Category.query.filter_by(name='Без категарії').first()
    if not default_category:
        default_category = Category(name='Без категарії')
        db.session.add(default_category)
        db.session.commit()
        logger.info("Создана категория 'Без категарії'")
    return default_category

@app.route('/admin/categories')
@login_required
@admin_required
def manage_categories():
    from models import Category
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/categories/add', methods=['POST'])
@login_required
@admin_required
def add_category():
    from models import Category
    try:
        name = request.form.get('name', '').strip()
        if not name:
            flash('Назва категорії обов\'язкова', 'error')
            return redirect(url_for('manage_categories'))
        
        # Проверяем, не существует ли уже такая категория
        if Category.query.filter_by(name=name).first():
            flash('Категорія з такою назвою вже існує', 'error')
            return redirect(url_for('manage_categories'))
        
        # Предотвращаем создание дубликатов "Без категарії"
        if name == 'Без категарії':
            flash('Категорія "Без категорії" вже існує в системі', 'error')
            return redirect(url_for('manage_categories'))
        
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        flash('Категорію успішно додано', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding category: {str(e)}")
        flash('Помилка при додаванні категорії', 'error')
    
    return redirect(url_for('manage_categories'))

@app.route('/admin/categories/<int:category_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_category(category_id):
    from models import Category, Material
    try:
        category = Category.query.get_or_404(category_id)
        
        # Логируем информацию для отладки
        logger.info(f"Попытка удаления категории: ID={category.id}, Имя='{category.name}'")
        
        # Проверяем, не пытаются ли удалить категорию "Без категарії"
        if category.name == 'Без категарії':
            logger.warning(f"Заблокировано удаление системной категории: {category.name}")
            return jsonify({
                'error': 'Неможливо видалити категорію "Без категарії". Це системна категорія.'
            }), 400
        
        # Получаем ID категории "Без категарії" напрямую из базы данных
        from sqlalchemy import text
        result = db.session.execute(text("SELECT id FROM category WHERE name = 'Без категарії'")).fetchone()
        
        if not result:
            logger.error("Категория 'Без категарії' не найдена!")
            return jsonify({
                'error': 'Системна категорія "Без категарії" не знайдена. Неможливо видалити категорію.'
            }), 500
        
        default_category_id = result[0]
        logger.info(f"ID категории 'Без категарії': {default_category_id}")
        
        if not default_category_id:
            logger.error("ID категории 'Без категарії' равен None!")
            return jsonify({
                'error': 'Помилка з ID системної категорії "Без категарії".'
            }), 500
        
        # Переносим все материалы удаляемой категории в "Без категарії" через прямой SQL
        materials_count_result = db.session.execute(
            text("SELECT COUNT(*) FROM materials WHERE category_id = :cat_id"),
            {'cat_id': category.id}
        ).fetchone()
        materials_count = materials_count_result[0] if materials_count_result else 0
        
        logger.info(f"Найдено {materials_count} материалов для переноса")
        
        if materials_count > 0:
            # Обновляем все материалы одним SQL-запросом
            logger.info(f"Переносим {materials_count} материалов из категории {category.id} в категорию {default_category_id}")
            db.session.execute(
                text("UPDATE materials SET category_id = :new_cat_id WHERE category_id = :old_cat_id"),
                {'new_cat_id': default_category_id, 'old_cat_id': category.id}
            )
        
        # Удаляем категорию
        logger.info(f"Удаляем категорию {category.id}")
        db.session.delete(category)
        db.session.commit()
        logger.info("Категория успешно удалена и материалы перенесены")
        
        # Формируем flash сообщение
        if materials_count > 0:
            flash(f'Категорію "{category.name}" успішно видалено. {materials_count} матеріалів перенесено до категорії "Без категарії".', 'success')
        else:
            flash(f'Категорію "{category.name}" успішно видалено.', 'success')
        
        return jsonify({
            'success': True,
            'redirect': url_for('manage_categories')
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting category: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'error': f'Помилка при видаленні категорії: {str(e)}'
        }), 500

@app.route('/admin/brands')
@login_required
@admin_required
def manage_brands():
    from models import Brand
    brands = Brand.query.all()
    return render_template('admin/brands.html', brands=brands)

@app.route('/admin/brands/<int:brand_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_brand(brand_id):
    from models import Brand, Material
    try:
        brand = Brand.query.get_or_404(brand_id)
        
        # Проверяем, есть ли материалы у этого бренда
        materials_count = Material.query.filter_by(brand_id=brand.id).count()
        if materials_count > 0:
            return jsonify({
                'error': f'Неможливо видалити бренд. Він містить {materials_count} матеріалів.'
            }), 400
        
        # Удаляем изображение бренда, если оно есть
        if brand.image_path and brand.image_path != 'default.png':
            image_path = os.path.join(app.static_folder, 'img', 'brands', brand.image_path)
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    logger.info(f"Removed brand image: {image_path}")
                except Exception as e:
                    logger.warning(f"Could not remove brand image: {e}")
        
        db.session.delete(brand)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Бренд успішно видалено'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting brand: {str(e)}")
        return jsonify({
            'error': 'Помилка при видаленні бренду'
        }), 500

@app.route('/admin/brands/<int:brand_id>/statistics')
@login_required
@admin_required
def brand_statistics(brand_id):
    """Детальная статистика по бренду"""
    from models import Brand
    brand = Brand.query.get_or_404(brand_id)
    user_stats = brand.get_user_statistics()
    
    return render_template('admin/brand_statistics.html', 
                         brand=brand, 
                         user_stats=user_stats)

@app.route('/admin/categories/<int:category_id>/statistics')
@login_required
@admin_required
def category_statistics(category_id):
    """Детальная статистика по категории"""
    from models import Category
    category = Category.query.get_or_404(category_id)
    user_stats = category.get_user_statistics()
    
    return render_template('admin/category_statistics.html', 
                         category=category, 
                         user_stats=user_stats)

@app.route('/admin/materials')
@login_required
@admin_required
def manage_materials():
    """Управление материалами - просмотр и статистика"""
    from models import Material
    materials = Material.query.all()
    return render_template('admin/materials.html', materials=materials)

@app.route('/admin/materials/<int:material_id>/statistics')
@login_required
@admin_required
def material_statistics(material_id):
    """Детальная статистика по материалу"""
    from models import Material
    material = Material.query.get_or_404(material_id)
    user_stats = material.get_user_statistics()
    
    return render_template('admin/material_statistics.html', 
                         material=material, 
                         user_stats=user_stats)

@app.route('/company_structure')
@login_required
def company_structure():
    """Страница структуры компании"""
    try:
        # Получаем всех пользователей
        all_users = User.query.all()
        
        # Разделяем пользователей по категориям
        founders = [user for user in all_users if user.department == 'founders']
        general_director = next((user for user in all_users if user.department == 'general_director'), None)
        
        # Структура отделов с их должностями
        department_structure = {
            'accounting': {
                'name': 'Відділ Бухгалтерії',
                'positions': {
                    'department_head': 'Керівник відділу',
                    'accountant': 'Бухгалтер'
                }
            },
            'marketing': {
                'name': 'Відділ Маркетингу',
                'positions': {
                    'department_head': 'Керівник відділу',
                    'photographer': 'Фотограф',
                    'marketer': 'Маркетолог'
                }
            },
            'online_sales': {
                'name': 'Відділ Онлайн продажу',
                'positions': {
                    'department_head': 'Керівник відділу',
                    'customer_manager': 'Менеджер по роботі з клієнтами'
                }
            },
            'offline_sales': {
                'name': 'Відділ Офлайн продажу',
                'positions': {
                    'department_head': 'Керівник відділу',
                    'seller': 'Продавець',
                    'cashier': 'Касир',
                    'merchandiser': 'Мерчендайзер'
                }
            },
            'foreign_trade': {
                'name': 'Відділ ЗЕД',
                'positions': {
                    'department_head': 'Керівник відділу',
                    'foreign_trade_manager': 'Менеджер ЗЕД'
                }
            },
            'warehouse': {
                'name': 'Складський відділ',
                'positions': {
                    'department_head': 'Керівник відділу',
                    'warehouse_worker': 'Комірник'
                }
            },
            'analytics': {
                'name': 'Відділ аналітики',
                'positions': {
                    'department_head': 'Керівник відділу',
                    'analyst': 'Аналітик'
                }
            },
            'abrams_production': {
                'name': 'Виробництво Abrams',
                'positions': {
                    'department_head': 'Керівник відділу',
                    'warehouse_worker': 'Комірник'
                }
            },
            'other': {
                'name': 'Інше',
                'positions': {
                    'office_manager': 'Офіс менеджер',
                    'cleaner': 'Прибиральниця',
                    'other_position': 'Інше'
                }
            }
        }
        
        # Группируем сотрудников по отделам
        departments = {}
        for dept_code, dept_info in department_structure.items():
            dept_employees = [user for user in all_users if user.department == dept_code]
            departments[dept_code] = {
                'name': dept_info['name'],
                'positions': dept_info['positions'],
                'employees': dept_employees
            }
        
        # Подсчитываем статистику
        total_employees = len(all_users)
        departments_count = len([dept for dept in departments.values() if dept['employees']])
        management_count = len([user for user in all_users if user.position == 'department_head'])
        
        # Подсчитываем вакантные позиции
        vacant_positions = 0
        for dept_info in departments.values():
            for position_code in dept_info['positions'].keys():
                position_employees = [emp for emp in dept_info['employees'] if emp.position == position_code]
                if not position_employees:
                    vacant_positions += 1
        
        return render_template('company_structure.html',
                             founders=founders,
                             founders_count=len(founders),
                             general_director=general_director,
                             departments=departments,
                             total_employees=total_employees,
                             departments_count=departments_count,
                             management_count=management_count,
                             vacant_positions=vacant_positions)
                             
    except Exception as e:
        logger.error(f"Error in company_structure: {str(e)}")
        flash('Помилка при завантаженні структури компанії', 'error')
        return redirect(url_for('index'))

@app.route('/orders')
@login_required
def orders():
    # Получаем все распоряжения
    all_orders = Order.query.order_by(Order.created_at.desc()).all()
    
    # DEBUG: Временно отключаем фильтрацию для диагностики
    filtered_orders = all_orders  # Показываем все заказы
    
    # Оригинальная фильтрация (временно отключена)
    # filtered_orders = []
    # for order in all_orders:
    #     # Администраторы видят все распоряжения
    #     if current_user.role == 'admin':
    #         filtered_orders.append(order)
    #     # Обычные пользователи видят только те распоряжения, которые предназначены для их отдела
    #     elif order.can_be_viewed_by_user(current_user):
    #         filtered_orders.append(order)
    
    # Получаем список отделов для фильтрации
    departments = User.DEPARTMENTS
    
    # DEBUG: Добавляем отладочную информацию
    print(f"DEBUG: Total orders: {len(all_orders)}")
    print(f"DEBUG: Filtered orders: {len(filtered_orders)}")
    if filtered_orders:
        print(f"DEBUG: First order: {filtered_orders[0].title}")
    
    return render_template('orders.html', 
                         orders=filtered_orders,
                         departments=departments)

@app.route('/orders/add', methods=['GET', 'POST'])
@login_required
def add_order():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        author_id = request.form.get('author_id')
        status = request.form.get('status', 'info')  # По умолчанию 'info'
        image = request.files.get('image')
        
        # Автоматически генерируем номер распоряжения
        # Находим последнее распоряжение по ID и увеличиваем номер на 1
        last_order = Order.query.order_by(Order.id.desc()).first()
        if last_order:
            next_number = last_order.id + 1
        else:
            next_number = 1
        
        # Форматируем номер как РОЗП-001, РОЗП-002 и т.д.
        number = f"РОЗП-{next_number:03d}"
        
        # Обрабатываем даты для статуса "До виконання"
        due_date_from = None
        due_date_to = None
        if status == 'todo':
            due_date_from_str = request.form.get('due_date_from')
            due_date_to_str = request.form.get('due_date_to')
            
            if due_date_from_str:
                try:
                    due_date_from = datetime.fromisoformat(due_date_from_str)
                except ValueError:
                    logger.warning(f"Invalid due_date_from format: {due_date_from_str}")
            
            if due_date_to_str:
                try:
                    due_date_to = datetime.fromisoformat(due_date_to_str)
                except ValueError:
                    logger.warning(f"Invalid due_date_to format: {due_date_to_str}")
            
            # Проверяем, что дата окончания позже даты начала
            if due_date_from and due_date_to and due_date_to <= due_date_from:
                flash('Дата завершення повинна бути пізніше дати початку', 'error')
                return redirect(url_for('add_order'))
        
        # Обрабатываем выбор отделов
        departments = []
        if request.form.get('all_departments'):
            departments = ['all']
        else:
            departments = request.form.getlist('departments')
        
        if not all([title, description, author_id, status]) or not departments:
            flash('Будь ласка, заповніть усі поля та виберіть відділи', 'error')
            return redirect(url_for('add_order'))
        
        try:
            # Сохраняем изображение, если оно есть
            image_path = None
            if image and image.filename:
                filename = secure_filename(image.filename)
                image_path = os.path.join(app.static_folder, 'img', 'orders', filename)
                # Создаем директорию, если её нет
                os.makedirs(os.path.dirname(image_path), exist_ok=True)
                image.save(image_path)
                image_path = filename
            
            # Получаем автора для определения его отдела (для обратной совместимости)
            author = User.query.get(author_id)
            author_department = author.department if author else 'other'
            
            order = Order(
                title=title,
                description=description,
                number=number,  # Используем автогенерированный номер
                department=author_department,  # Старое поле для совместимости
                departments=departments,  # Новое поле со списком отделов
                author_id=author_id,
                status=status,
                due_date_from=due_date_from,
                due_date_to=due_date_to,
                image_path=image_path
            )
            db.session.add(order)
            db.session.commit()
            flash(f'Розпорядження {number} успішно додано', 'success')
            return redirect(url_for('orders'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding order: {str(e)}")
            flash('Помилка при додаванні розпорядження', 'error')
            return redirect(url_for('add_order'))
    
    # Для GET запроса получаем руководителей
    leaders = User.query.filter(
        User.position.in_(['founder', 'general_director', 'department_head'])
    ).all()
    
    return render_template('order_add.html', 
                         departments=User.DEPARTMENTS, 
                         leaders=leaders)

@app.route('/orders/<int:order_id>')
@login_required
def view_order(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('order_view.html', order=order)

@app.route('/orders/<int:order_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_order(order_id):
    order = Order.query.get_or_404(order_id)
    
    # Проверяем права доступа
    if current_user.role != 'admin' and order.author_id != current_user.id:
        flash('У вас немає прав для редагування цього розпорядження', 'error')
        return redirect(url_for('orders'))
    
    if request.method == 'POST':
        try:
            # Обновляем основные данные
            order.title = request.form.get('title')
            order.description = request.form.get('description')
            # order.number - номер не изменяется, генерируется автоматически
            order.author_id = request.form.get('author_id')
            order.status = request.form.get('status')
            
            # Обрабатываем даты для статуса "До виконання"
            if order.status == 'todo':
                due_date_from_str = request.form.get('due_date_from')
                due_date_to_str = request.form.get('due_date_to')
                
                order.due_date_from = None
                order.due_date_to = None
                
                if due_date_from_str:
                    try:
                        order.due_date_from = datetime.fromisoformat(due_date_from_str)
                    except ValueError:
                        logger.warning(f"Invalid due_date_from format: {due_date_from_str}")
                
                if due_date_to_str:
                    try:
                        order.due_date_to = datetime.fromisoformat(due_date_to_str)
                    except ValueError:
                        logger.warning(f"Invalid due_date_to format: {due_date_to_str}")
                
                # Проверяем, что дата окончания позже даты начала
                if order.due_date_from and order.due_date_to and order.due_date_to <= order.due_date_from:
                    flash('Дата завершення повинна бути пізніше дати початку', 'error')
                    return redirect(url_for('edit_order', order_id=order_id))
            else:
                # Если статус не "todo", очищаем даты
                order.due_date_from = None
                order.due_date_to = None
            
            # Обрабатываем выбор отделов
            departments = []
            if request.form.get('all_departments'):
                departments = ['all']
            else:
                departments = request.form.getlist('departments')
            
            if not departments:
                flash('Будь ласка, виберіть відділи', 'error')
                return redirect(url_for('edit_order', order_id=order_id))
            
            order.departments = departments
            
            # Обновляем отдел автора для обратной совместимости
            author = User.query.get(order.author_id)
            if author:
                order.department = author.department
            
            db.session.commit()
            flash('Розпорядження успішно оновлено', 'success')
            return redirect(url_for('orders'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating order: {str(e)}")
            flash('Помилка при оновленні розпорядження', 'error')
    
    # Для GET запроса получаем руководителей
    leaders = User.query.filter(
        User.position.in_(['founder', 'general_director', 'department_head'])
    ).all()
    
    return render_template('order_edit.html', 
                         order=order, 
                         departments=User.DEPARTMENTS,
                         leaders=leaders)

@app.route('/orders/<int:order_id>/delete', methods=['POST'])
@login_required
def delete_order(order_id):
    logger.info(f"=== Начало удаления распоряжения {order_id} ===")
    try:
        # Проверяем права доступа
        order = Order.query.get_or_404(order_id)
        if current_user.role != 'admin' and order.author_id != current_user.id:
            logger.warning(f"Попытка удаления распоряжения {order_id} пользователем без прав")
            return jsonify({'error': 'У вас немає прав для видалення цього розпорядження'}), 403

        # Получаем CSRF-токен из JSON-данных
        data = request.get_json()
        logger.info(f"Полученные данные: {data}")
        
        if not data or 'csrf_token' not in data:
            logger.error("CSRF token missing")
            return jsonify({'error': 'CSRF token missing'}), 400

        try:
            validate_csrf(data['csrf_token'])
        except Exception as e:
            logger.error(f"CSRF validation error: {str(e)}")
            return jsonify({'error': 'Invalid CSRF token'}), 400

        # Если это первый запрос на удаление, возвращаем запрос подтверждения
        if not data.get('confirmed'):
            logger.info("Запрашиваем подтверждение удаления")
            return jsonify({
                'needs_confirmation': True,
                'order_title': order.title,
                'order_number': order.number
            })

        # Если пользователь подтвердил удаление
        if data.get('confirmed'):
            logger.info("Начинаем процесс удаления распоряжения")
            try:
                # Удаляем изображение, если есть
                if order.image_path:
                    try:
                        image_path = os.path.join(app.static_folder, 'img', 'orders', order.image_path)
                        logger.info(f"Удаляем изображение: {image_path}")
                        if os.path.exists(image_path):
                            os.remove(image_path)
                    except Exception as e:
                        logger.warning(f"Ошибка при удалении изображения: {e}")

                # Удаляем само распоряжение
                logger.info("Удаляем распоряжение из базы данных")
                db.session.delete(order)
                db.session.commit()
                logger.info("Распоряжение успешно удалено")

                return jsonify({
                    'success': True,
                    'redirect': url_for('orders'),
                    'message': 'Розпорядження було успішно видалено'
                })

            except Exception as e:
                db.session.rollback()
                logger.error(f"Ошибка при удалении распоряжения: {str(e)}")
                return jsonify({
                    'error': 'Помилка при видаленні розпорядження',
                    'details': str(e)
                }), 500

    except Exception as e:
        logger.error(f"Непредвиденная ошибка в delete_order: {str(e)}")
        return jsonify({
            'error': 'Помилка при видаленні розпорядження',
            'details': str(e)
        }), 500
    finally:
        logger.info(f"=== Завершение удаления распоряжения {order_id} ===")

@app.route('/static/img/users/<path:filename>')
def serve_user_photo(filename):
    try:
        # Сначала пробуем найти файл в папке users
        file_path = os.path.join(app.static_folder, 'img', 'users', filename)
        logger.info(f"Пытаемся найти файл: {file_path}")
        
        if os.path.exists(file_path):
            logger.info(f"Файл найден: {file_path}")
            return send_from_directory(os.path.join(app.static_folder, 'img', 'users'), filename)
        
        # Если файл не найден, возвращаем изображение по умолчанию
        default_path = os.path.join(app.static_folder, 'img', 'users', 'default.png')
        logger.info(f"Файл {filename} не найден, используем изображение по умолчанию: {default_path}")
        
        if os.path.exists(default_path):
            return send_from_directory(os.path.join(app.static_folder, 'img', 'users'), 'default.png')
        else:
            logger.error(f"Файл по умолчанию не найден: {default_path}")
            return "File not found", 404
            
    except Exception as e:
        logger.error(f"Ошибка при загрузке фотографии пользователя {filename}: {str(e)}")
        return "Internal server error", 500

@app.route('/category/<int:category_id>')
def category(category_id):
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    per_page = 12  # Количество материалов на странице
    
    # Получаем материалы с пагинацией, сортируем по дате в обратном порядке
    materials_pagination = Material.query.filter_by(category_id=category_id)\
        .order_by(Material.id.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    # Получаем все бренды для фильтрации
    brands = Brand.query.all()
    
    return render_template('category.html', 
                         category=category, 
                         materials=materials_pagination.items,
                         pagination=materials_pagination,
                         brands=brands)

@app.route('/upload-image', methods=['POST'])
@login_required
def upload_image():
    """Роут для завантаження зображень з CKEditor"""
    try:
        logger.info("Отримано запит на завантаження зображення")
        
        # Проверяем CSRF токен вручную
        try:
            validate_csrf(request.form.get('csrf_token', ''))
        except:
            # Если CSRF токен в форме не найден, пробуем в заголовках
            csrf_token = request.headers.get('X-CSRFToken') or request.headers.get('X-Requested-With')
            if not csrf_token:
                logger.error("CSRF токен не знайдено")
                return jsonify({"error": {"message": "CSRF token missing"}}), 403
        
        if 'upload' not in request.files:
            logger.error("Файл не знайдено в запиті")
            return jsonify({"error": {"message": "No file part"}}), 400

        file = request.files['upload']
        if file.filename == '':
            logger.error("Файл не обрано")
            return jsonify({"error": {"message": "No selected file"}}), 400

        if file:
            # Используем нашу комплексную валидацию файла
            is_valid, error_message = validate_image_file(file)
            if not is_valid:
                logger.error(f"Файл не прошел валидацию: {error_message}")
                return jsonify({"error": {"message": error_message}}), 400
            
            # Генерируем безопасное имя файла
            unique_filename = generate_secure_filename(file.filename)
            
            # Шлях для збереження
            upload_folder = os.path.join(app.static_folder, 'uploads')
            filepath = os.path.join(upload_folder, unique_filename)
            
            # Зберігаємо файл
            file.save(filepath)
            logger.info(f"Файл збережено: {filepath}")
            
            # Генеруємо URL для зображення
            file_url = url_for('static', filename=f'uploads/{unique_filename}', _external=True)
            logger.info(f"URL зображення: {file_url}")
            
            # Повертаємо відповідь у форматі, очікуваному CKFinder
            return jsonify({
                'uploaded': True,
                'url': file_url
            })
            
    except Exception as e:
        logger.error(f"Ошибка при загрузке изображения: {str(e)}")
        return jsonify({"error": {"message": "Upload failed"}}), 500

# Запуск приложения
if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            logger.info("База данных инициализирована")
        except Exception as e:
            logger.error(f"Ошибка инициализации базы данных: {e}")
    
    # Запуск в зависимости от окружения
    if os.getenv('FLASK_ENV') == 'production':
        # В продакшене приложение запускается через gunicorn
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    else:
        # В разработке - с отладкой
        app.run(debug=True, host='127.0.0.1', port=5000)
