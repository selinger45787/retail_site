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