from flask import Flask, render_template, redirect, url_for, request, flash, send_from_directory, jsonify, current_app, session
import os
import markupsafe
from models import db, User, Brand, Material, Category, MaterialImage, Test, TestQuestion, TestAnswer, TestResult, TestQuestionResult, TestAssignment
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
from forms import AddUserForm, LoginForm, TestAssignmentForm, EditTestAssignmentForm
from functools import wraps

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация приложения
app = Flask(__name__)

# Базовые настройки
app.config.from_object(config['development'])

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

app.jinja_env.filters['nl2br'] = nl2br

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
    per_page = 12  # Количество материалов на странице
    
    # Получаем материалы с пагинацией, сортируем по дате в обратном порядке
    materials_pagination = Material.query.filter_by(brand_id=brand_id)\
        .order_by(Material.id.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('brand.html', 
                         brand=brand, 
                         materials=materials_pagination.items,
                         pagination=materials_pagination)

@app.route('/brand/<int:brand_id>/info')
def brand_info(brand_id):
    brand = Brand.query.get_or_404(brand_id)
    return render_template('brand_info.html', brand=brand)

@app.route('/brand/<int:brand_id>/history')
def brand_history(brand_id):
    brand = Brand.query.get_or_404(brand_id)
    return render_template('brand_history.html', brand=brand)

@app.route('/add_material', defaults={'brand_id': None}, methods=['GET', 'POST'])
@app.route('/brand/<int:brand_id>/add_material', methods=['GET', 'POST'])
def add_material(brand_id):
    categories = Category.query.all()
    brands = Brand.query.all()
    
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
            logger.error(f"Отсутствуют обязательные поля: {missing_fields}")
            if request.headers.get('Accept') == 'application/json':
                return jsonify({'error': 'Будь ласка, заповніть всі обов\'язкові поля'}), 400
            flash('Будь ласка, заповніть всі обов\'язкові поля', 'error')
            return redirect(url_for('add_material', brand_id=brand_id))
        
        try:
            # Сохраняем главное изображение
            main_image_path = None
            if main_image and main_image.filename:
                filename = secure_filename(main_image.filename)
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
                    filename = secure_filename(image.filename)
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
                    'redirect': url_for('brand', brand_id=brand_id)
                })
            
            flash('Матеріал успішно додано', 'success')
            return redirect(url_for('brand', brand_id=brand_id))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Ошибка при сохранении материала: {str(e)}")
            if request.headers.get('Accept') == 'application/json':
                return jsonify({'error': 'Помилка при додаванні матеріалу'}), 500
            flash('Помилка при додаванні матеріалу', 'error')
            return redirect(url_for('add_material', brand_id=brand_id))
    
    # Для GET запроса
    brand = None
    if brand_id:
        brand = Brand.query.get_or_404(brand_id)
    
    return render_template('material_add.html', 
                         brand=brand,
                         brands=brands,
                         categories=categories,
                         show_brand_select=brand_id is None)

@app.route('/material/<int:material_id>')
def view_material(material_id):
    material = Material.query.get_or_404(material_id)
    images = MaterialImage.query.filter_by(material_id=material_id).all()
    
    return render_template('material.html', 
                         material=material, 
                         images=images)

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
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.static_folder, 'img', 'materials', filename)
                    file.save(file_path)
                    material.image_path = filename
            
            # Обрабатываем дополнительные изображения
            if 'additional_images' in request.files:
                files = request.files.getlist('additional_images')
                for file in files:
                    if file and file.filename:
                        filename = secure_filename(file.filename)
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
        if current_user.role != 'admin':
            logger.warning(f"Попытка удаления материала {material_id} пользователем без прав админа")
            return jsonify({'error': 'У вас немає прав для видалення матеріалів', 'redirect': url_for('view_material', material_id=material_id)}), 403

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

        # Если это первый запрос на удаление, возвращаем информацию о зависимостях
        if not data.get('confirmed'):
            logger.info("Возвращаем информацию о зависимостях")
            return jsonify({
                'has_test': has_test,
                'has_active_assignments': has_active_assignments,
                'active_assignments_count': active_assignments,
                'needs_confirmation': True
            })

        # Если пользователь подтвердил удаление
        if data.get('confirmed'):
            logger.info("Начинаем процесс удаления")
            try:
                # Сначала удаляем все связанные результаты тестов
                if test:
                    logger.info("Удаляем связанные результаты теста")
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

                # Удаляем все назначения теста
                TestAssignment.query.filter_by(material_id=material_id).delete()
                logger.info("Назначения теста удалены")

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
        
        if not name:
            if request.headers.get('Accept') == 'application/json':
                return jsonify({'error': 'Назва бренду обов\'язкова'}), 400
            flash('Назва бренду обов\'язкова', 'error')
            return redirect(url_for('index'))
        
        # Проверяем, существует ли бренд с таким названием
        existing_brand = Brand.query.filter_by(name=name).first()
        if existing_brand:
            if request.headers.get('Accept') == 'application/json':
                return jsonify({'error': 'Бренд з такою назвою вже існує'}), 400
            flash('Бренд з такою назвою вже існує', 'error')
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
            
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            if request.headers.get('Accept') == 'application/json':
                return jsonify({'error': 'Помилка при додаванні бренду'}), 500
            flash('Помилка при додаванні бренду', 'error')
            app.logger.error(f'Error adding brand: {str(e)}')
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
        flash('У вас нет прав для создания тестов', 'danger')
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
        max_score=total_questions
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
        flash('У вас нет прав для редактирования тестов', 'error')
        return redirect(url_for('view_material', material_id=material_id))
    
    material = Material.query.get_or_404(material_id)
    test = Test.query.filter_by(material_id=material_id).first()
    
    if not test:
        flash('Тест не найден', 'error')
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
            flash('Тест успешно обновлен', 'success')
            return redirect(url_for('view_material', material_id=material_id))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Ошибка при обновлении теста: {str(e)}")
            logger.error(f"Тип ошибки: {type(e)}")
            logger.error(f"Детали ошибки: {traceback.format_exc()}")
            flash('Произошла ошибка при обновлении теста', 'error')
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
    
    # Для администратора получаем статистику всех пользователей
    all_users_stats = None
    if current_user.role == 'admin':
        all_users_stats = []
        for user in User.query.all():
            user_results = TestResult.query.filter_by(user_id=user.id).all()
            
            user_total = len(user_results)
            user_passed = sum(1 for r in user_results if r.score >= 80)
            user_failed = user_total - user_passed
            user_avg = sum(r.score for r in user_results) / user_total if user_total > 0 else 0
            
            all_users_stats.append({
                'username': user.username,
                'total_tests': user_total,
                'passed_tests': user_passed,
                'failed_tests': user_failed,
                'avg_score': round(user_avg, 1)
            })
    
    return render_template('user_profile.html', 
                        user=user,
                        test_results=test_results,
                        total_tests=total_tests,
                        passed_tests=passed_tests,
                        failed_tests=failed_tests,
                        avg_score=round(avg_score, 1),
                        all_users_stats=all_users_stats)

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
        
        # Статистика по времени (последние 30 дней)
        time_data = {}
        today = datetime.utcnow().date()
        for i in range(30):
            date = today - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            time_data[date_str] = {
                'count': 0,
                'sum_score': 0,
                'avg_score': 0
            }
        
        for result in test_results:
            date_str = result.created_at.strftime('%Y-%m-%d')
            if date_str in time_data:
                time_data[date_str]['count'] += 1
                time_data[date_str]['sum_score'] += result.score
        
        # Рассчитываем средний балл для каждого дня
        for date_str in time_data:
            if time_data[date_str]['count'] > 0:
                time_data[date_str]['avg_score'] = time_data[date_str]['sum_score'] / time_data[date_str]['count']
        
        # Превращаем словарь в список для шаблона, сортируем по дате
        chart_data = [{'date': date, 'value': data['avg_score']} for date, data in time_data.items()]
        chart_data.sort(key=lambda x: x['date'])
        
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
                        'avg_score': 0
                    }
            
            if test_id in tests_stats:
                tests_stats[test_id]['scores'].append(result.score)
        
        # Рассчитываем средний балл для каждого теста
        for test_id in tests_stats:
            scores = tests_stats[test_id]['scores']
            tests_stats[test_id]['avg_score'] = sum(scores) / len(scores) if scores else 0
        
        # Сортируем тесты по среднему баллу (по возрастанию)
        problematic_tests = sorted(
            [{'test': data['test'], 'avg_score': data['avg_score']} for test_id, data in tests_stats.items()],
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
                        'avg_score': 0
                    }
            
            if user_id in users_stats:
                users_stats[user_id]['scores'].append(result.score)
        
        # Рассчитываем средний балл для каждого пользователя
        for user_id in users_stats:
            scores = users_stats[user_id]['scores']
            users_stats[user_id]['avg_score'] = sum(scores) / len(scores) if scores else 0
        
        # Сортируем пользователей по среднему баллу (по возрастанию)
        problematic_users = sorted(
            [{'user': data['user'], 'avg_score': data['avg_score']} for user_id, data in users_stats.items()],
            key=lambda x: x['avg_score']
        )[:5]  # Топ-5 проблемных пользователей
        
        return render_template('admin_dashboard.html',
                             users=users,
                             total_attempts=total_attempts,
                             avg_score=round(avg_score, 1),
                             success_rate=round(success_rate, 1),
                             chart_data=chart_data,
                             problematic_tests=problematic_tests,
                             problematic_users=problematic_users)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in admin_dashboard: {str(e)}")
        flash('Произошла ошибка при загрузке панели администратора', 'error')
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
                'question_details': question_details
            }
            
            brands_data[brand.id]['materials'][material.id]['attempts'].append(attempt_data)
            logger.info(f"Added attempt with score {result.score}% to material {material.title}")
        
        # Преобразуем словари в списки для удобства использования в шаблоне
        brands_list = []
        for brand_id, brand_data in brands_data.items():
            materials_list = []
            for material_id, material_data in brand_data['materials'].items():
                materials_list.append({
                    'id': material_id,
                    'title': material_data['title'],
                    'attempts': material_data['attempts']
                })
            brands_list.append({
                'id': brand_id,
                'name': brand_data['name'],
                'materials': materials_list
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
    logger.error(f"Произошла ошибка: {str(error)}")
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
            
            # Create new user
            user = User(
                username=form.username.data,
                role=form.role.data,
                phone_number=form.phone_number.data,
                department=form.department.data,
                position=form.position.data
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
    if form.validate_on_submit():
        try:
            # Проверяем, что дата окончания позже даты начала
            if form.end_date.data <= form.start_date.data:
                flash('Дата окончания должна быть позже даты начала', 'error')
                return redirect(url_for('test_assignments'))
            
            # Проверяем, что у материала есть тест
            material = Material.query.get(form.material_id.data)
            if not Test.query.filter_by(material_id=material.id).first():
                flash('Для этого материала еще не создан тест', 'error')
                return redirect(url_for('test_assignments'))
            
            # Проверяем, нет ли уже активного назначения для этого пользователя и материала
            existing_assignment = TestAssignment.query.filter(
                TestAssignment.user_id == form.user_id.data,
                TestAssignment.material_id == form.material_id.data,
                TestAssignment.is_completed == False
            ).first()
            
            if existing_assignment:
                flash('Цьому користувачу вже призначено цей тест', 'error')
                return redirect(url_for('test_assignments'))
            
            # Создаем новое назначение
            assignment = TestAssignment(
                user_id=form.user_id.data,
                material_id=form.material_id.data,
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                created_by=current_user.id
            )
            
            db.session.add(assignment)
            db.session.commit()
            
            flash('Тест успешно назначен', 'success')
            return redirect(url_for('test_assignments'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating test assignment: {str(e)}")
            flash('Произошла ошибка при назначении теста', 'error')

    assignments = TestAssignment.query.order_by(TestAssignment.created_at.desc()).all()
    return render_template('test_assignments.html', 
                         form=form, 
                         assignments=assignments,
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
                flash('Дата окончания должна быть позже даты начала', 'error')
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
            flash('Произошла ошибка при обновлении дат', 'error')
    
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
        db.session.execute('SELECT 1')
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
    form = AddUserForm(obj=user)
    
    if request.method == 'POST':
        if form.validate_on_submit():
            user.username = form.username.data
            if form.password.data:  # Обновляем пароль только если он был изменен
                user.set_password(form.password.data)
            user.role = form.role.data
            user.phone_number = form.phone_number.data
            user.department = form.department.data
            user.position = form.position.data
            
            try:
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

if __name__ == '__main__':
    app.run(debug=True)
