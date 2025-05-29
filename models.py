from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False, default='user')  # 'admin' or 'user'
    phone_number = db.Column(db.String(20))
    department = db.Column(db.String(50))  # 'online', 'offline', 'office', 'management'
    position = db.Column(db.String(50))  # 'seller', 'cashier', 'manager', 'merchandiser', 'other'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    test_results = db.relationship('TestResult', backref='test_user', lazy=True)
    
    # Словарь соответствия кодов отделов и их названий
    DEPARTMENTS = {
        'founders': 'Засновники компанії',
        'general_director': 'Генеральний директор',
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
    
    # Словарь соответствия кодов должностей и их названий
    POSITIONS = {
        'founder': 'Засновник',
        'general_director': 'Генеральний директор',
        'department_head': 'Керівник відділу',
        'accountant': 'Бухгалтер',
        'photographer': 'Фотограф',
        'marketer': 'Маркетолог',
        'customer_manager': 'Менеджер по роботі з клієнтами',
        'seller': 'Продавець',
        'cashier': 'Касир',
        'merchandiser': 'Мерчендайзер',
        'foreign_trade_manager': 'Менеджер ЗЕД',
        'warehouse_worker': 'Комірник',
        'analyst': 'Аналітик',
        'office_manager': 'Офіс менеджер',
        'cleaner': 'Прибиральниця',
        'other_position': 'Інше'
    }
    
    @property
    def department_name(self):
        """Возвращает читаемое название отдела"""
        return self.DEPARTMENTS.get(self.department, self.department)
    
    @property
    def position_name(self):
        """Возвращает читаемое название должности"""
        return self.POSITIONS.get(self.position, self.position)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Brand(db.Model):
    __tablename__ = 'brands'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    materials = db.relationship('Material', backref='brand', lazy=True)

    def __repr__(self):
        return f'<Brand {self.name}>'

class MaterialImage(db.Model):
    __tablename__ = 'material_images'
    
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(255), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<MaterialImage {self.id}>'

class Material(db.Model):
    __tablename__ = 'materials'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image_path = db.Column(db.String(255))  # Основное изображение
    date = db.Column(db.DateTime, default=datetime.utcnow)
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    
    # Добавляем связь с изображениями
    images = db.relationship('MaterialImage', backref='material', lazy=True, cascade='all, delete-orphan')
    
    def get_user_test_result(self, user_id):
        """Получает последний результат теста пользователя для этого материала"""
        if not self.tests:
            return None
        
        # Получаем последний результат теста для этого материала
        from sqlalchemy import desc
        result = TestResult.query.filter_by(
            user_id=user_id,
            test_id=self.tests[0].id
        ).order_by(desc(TestResult.created_at)).first()
        
        return result
    
    def __repr__(self):
        return f'<Material {self.title}>'

class Category(db.Model):
    __tablename__ = 'category'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    materials = db.relationship('Material', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'

class Test(db.Model):
    __tablename__ = 'tests'
    
    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Связи
    material = db.relationship('Material', backref='tests')
    questions = db.relationship('TestQuestion', backref='test', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Test {self.id} for Material {self.material_id}>'

class TestQuestion(db.Model):
    __tablename__ = 'test_question'
    
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id', ondelete='CASCADE'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Обновляем связь с ответами
    answers = db.relationship('TestAnswer', back_populates='question', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<TestQuestion {self.id}>'

class TestAnswer(db.Model):
    __tablename__ = 'test_answer'
    
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('test_question.id', ondelete='CASCADE'), nullable=False)
    text = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Добавляем явную связь с вопросом
    question = db.relationship('TestQuestion', back_populates='answers')
    
    def __repr__(self):
        return f'<TestAnswer {self.id}>'

class TestResult(db.Model):
    __tablename__ = 'test_result'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    max_score = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    test = db.relationship('Test', backref=db.backref('test_results', lazy=True))

class TestQuestionResult(db.Model):
    __tablename__ = 'test_question_result'
    id = db.Column(db.Integer, primary_key=True)
    test_result_id = db.Column(db.Integer, db.ForeignKey('test_result.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('test_question.id'), nullable=False)
    answer_given = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    test_result = db.relationship('TestResult', backref=db.backref('question_results', lazy=True))
    question = db.relationship('TestQuestion', backref=db.backref('question_results', lazy=True))

class TestAssignment(db.Model):
    __tablename__ = 'test_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Связи
    user = db.relationship('User', foreign_keys=[user_id], backref='test_assignments')
    material = db.relationship('Material', backref='test_assignments')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_assignments')

    def __repr__(self):
        return f'<TestAssignment {self.id}: {self.user.username} - {self.material.title}>'

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    number = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image_path = db.Column(db.String(255))
    
    author = db.relationship('User', backref=db.backref('orders', lazy=True))
    
    @property
    def status_name(self):
        status_names = {
            'active': 'Активне',
            'completed': 'Виконане',
            'cancelled': 'Скасоване'
        }
        return status_names.get(self.status, self.status)

    @property
    def status_color(self):
        status_colors = {
            'active': 'primary',
            'completed': 'success',
            'cancelled': 'danger'
        }
        return status_colors.get(self.status, 'secondary')

    @property
    def department_name(self):
        return User.DEPARTMENTS.get(self.department, self.department)

    @property
    def author_name(self):
        return self.author.username if self.author else 'Невідомий'
    
    def __repr__(self):
        return f'<Order {self.number}: {self.title}>'