from flask import Flask, render_template, redirect, url_for, request, flash, send_from_directory, jsonify
import os
import markupsafe
from models import db, User, Brand, Material, Category, MaterialImage
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import logging
from config import config
from datetime import datetime
from flask_migrate import Migrate
import bleach

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация приложения
app = Flask(__name__)

# Базовые настройки
app.config.from_object(config['development'])

# Создаем необходимые папки
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.static_folder, 'img', 'materials'), exist_ok=True)
os.makedirs(os.path.join(app.static_folder, 'img', 'brands'), exist_ok=True)
os.makedirs(os.path.join(app.static_folder, 'img', 'icons'), exist_ok=True)

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
    return User.query.get(int(user_id))

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
        logger.error(f"Error loading brands: {str(e)}")
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
        if os.path.exists(file_path):
            return send_from_directory(os.path.join(app.static_folder, 'img', 'materials'), filename)
        
        # Если файл не найден, возвращаем изображение по умолчанию
        logger.info(f"Файл {filename} не найден, используем изображение по умолчанию")
        return send_from_directory(os.path.join(app.static_folder, 'img', 'materials'), 'default.png')
    except Exception as e:
        logger.error(f"Ошибка при загрузке изображения {filename}: {str(e)}")
        return send_from_directory(os.path.join(app.static_folder, 'img', 'materials'), 'default.png')

def nl2br(value):
    if not value:
        return ''
    return markupsafe.Markup(value.replace('\n', '<br>'))

app.jinja_env.filters['nl2br'] = nl2br

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/brand/<int:brand_id>')
def brand(brand_id):
    brand = Brand.query.get_or_404(brand_id)
    page = request.args.get('page', 1, type=int)
    per_page = 9  # Количество материалов на странице
    
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
        description = request.form.get('description')
        category_id = request.form.get('category_id')
        main_image = request.files.get('image')
        additional_images = request.files.getlist('additional_images')
        
        logger.info(f"Полученные данные: title={title}, category_id={category_id}")
        logger.info(f"Описание материала (raw): {description}")
        
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
            flash('Будь ласка, заповніть всі обов\'язкові поля', 'error')
            return redirect(url_for('add_material', brand_id=brand_id))
        
        try:
            # Очищаем HTML от потенциально опасных тегов и атрибутов
            cleaned_description = bleach.clean(
                description,
                tags=ALLOWED_TAGS,
                attributes=ALLOWED_ATTRIBUTES,
                strip=True
            )
            logger.info(f"Очищенное описание: {cleaned_description}")
            
            # Сохраняем главное изображение
            main_image_path = None
            if main_image and main_image.filename:
                filename = secure_filename(main_image.filename)
                image_path = os.path.join(app.static_folder, 'img', 'materials', filename)
                main_image.save(image_path)
                main_image_path = filename
                logger.info(f"Сохранено главное изображение: {filename}")
            
            # Создаем новый материал
            material = Material(
                title=title,
                description=cleaned_description,  # Используем очищенный HTML
                image_path=main_image_path,
                brand_id=brand_id,
                category_id=category_id
            )
            
            db.session.add(material)
            db.session.flush()
            logger.info(f"Создан новый материал с ID: {material.id}")
            logger.info(f"Сохраненное описание: {material.description}")
            
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
                    logger.info(f"Добавлено дополнительное изображение: {filename}")
            
            db.session.commit()
            logger.info("Материал успешно сохранен в базу данных")
            
            flash('Матеріал успішно додано', 'success')
            return redirect(url_for('brand', brand_id=brand_id))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Ошибка при сохранении материала: {str(e)}")
            flash('Помилка при додаванні матеріалу', 'error')
            return redirect(url_for('add_material', brand_id=brand_id))
    
    # Для GET запроса
    brand = None
    if brand_id:
        brand = Brand.query.get_or_404(brand_id)
    
    return render_template('add_material.html', 
                         brand=brand,
                         brands=brands,
                         categories=categories,
                         show_brand_select=brand_id is None)

@app.route('/brand/<int:brand_id>/edit', methods=['POST'])
@login_required
def edit_brand(brand_id):
    if current_user.role != 'admin':
        flash('У вас немає прав для цієї дії', 'error')
        return redirect(url_for('brand', brand_id=brand_id))
    
    brand = Brand.query.get_or_404(brand_id)
    
    try:
        brand.name = request.form['name']
        
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                brand.image_path = filename
        
        db.session.commit()
        flash('Бренд успішно оновлено', 'success')
    except Exception as e:
        logger.error(f"Помилка при оновленні бренду: {str(e)}")
        flash('Помилка при оновленні бренду', 'error')
    
    return redirect(url_for('brand', brand_id=brand_id))

@app.route('/materials')
def materials():
    materials = Material.query.all()
    return render_template('materials.html', materials=materials)

@app.route('/material/<int:material_id>')
def view_material(material_id):
    material = Material.query.get_or_404(material_id)
    # Загружаем дополнительные изображения
    additional_images = MaterialImage.query.filter_by(material_id=material_id).all()
    material.additional_images = additional_images
    return render_template('material.html', material=material)

@app.route('/material/<int:material_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_material(material_id):
    material = Material.query.get_or_404(material_id)
    if request.method == 'POST':
        material.name = request.form.get('name')
        material.description = request.form.get('description')
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                material.image_path = filename
        db.session.commit()
        flash('Материал успешно обновлен', 'success')
        return redirect(url_for('view_material', material_id=material.id))
    return render_template('edit_material.html', material=material)

@app.route('/material/<int:material_id>/delete', methods=['POST'])
@login_required
def delete_material(material_id):
    material = Material.query.get_or_404(material_id)
    db.session.delete(material)
    db.session.commit()
    flash('Материал успешно удален', 'success')
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            if request.headers.get('Accept') == 'application/json':
                return jsonify({'success': True})
            flash('Ви успішно увійшли в систему', 'success')
            return redirect(url_for('index'))
            
        if request.headers.get('Accept') == 'application/json':
            return jsonify({'error': 'Невірний логін або пароль'})
        flash('Невірний логін або пароль', 'error')
            
    return render_template('login.html')

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
    return send_from_directory(os.path.join(app.static_folder, 'img', 'icons'),
                             'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/add_brand', methods=['POST'])
@login_required
def add_brand():
    if request.method == 'POST':
        name = request.form.get('name')
        image = request.files.get('image')
        
        if not name:
            flash('Назва бренду обов\'язкова', 'error')
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
            flash('Бренд успішно додано', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Помилка при додаванні бренду', 'error')
            app.logger.error(f'Error adding brand: {str(e)}')
        
        return redirect(url_for('index'))

@app.errorhandler(Exception)
def handle_error(error):
    logger.error(f"Произошла ошибка: {str(error)}")
    return render_template('error.html', error=error), 500

if __name__ == '__main__':
    app.run(debug=True)
