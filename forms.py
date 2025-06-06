from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SelectField, SubmitField, DateTimeField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from models import User, Material, Test

class AddUserForm(FlaskForm):
    username = StringField('Ім\'я користувача', validators=[DataRequired(), Length(min=2, max=50)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Підтвердження паролю', 
                                   validators=[DataRequired(), EqualTo('password')])
    phone_number = StringField('Номер телефону', 
                             validators=[DataRequired(), Length(min=9, max=9)],
                             render_kw={"placeholder": "Введіть 9 цифр"})
    role = SelectField('Доступ', 
                      choices=[
                          ('user', 'Користувач'),
                          ('admin', 'Адміністратор')
                      ],
                      validators=[DataRequired()])
    department = SelectField('Відділ',
                           choices=[
                               ('founders', 'Засновники компанії'),
                               ('general_director', 'Генеральний директор'),
                               ('accounting', 'Відділ Бухгалтерії'),
                               ('marketing', 'Відділ Маркетингу'),
                               ('online_sales', 'Відділ Онлайн продажу'),
                               ('offline_sales', 'Відділ Офлайн продажу'),
                               ('foreign_trade', 'Відділ ЗЕД'),
                               ('warehouse', 'Складський відділ'),
                               ('analytics', 'Відділ аналітики'),
                               ('other', 'Інше'),
                               ('abrams_production', 'Виробництво Abrams')
                           ],
                           validators=[DataRequired()])
    position = SelectField('Посада',
                         choices=[
                             ('founder', 'Засновник'),
                             ('general_director', 'Генеральний директор'),
                             ('department_head', 'Керівник відділу'),
                             ('accountant', 'Бухгалтер'),
                             ('photographer', 'Фотограф'),
                             ('marketer', 'Маркетолог'),
                             ('customer_manager', 'Менеджер по роботі з клієнтами'),
                             ('seller', 'Продавець'),
                             ('cashier', 'Касир'),
                             ('merchandiser', 'Мерчендайзер'),
                             ('foreign_trade_manager', 'Менеджер ЗЕД'),
                             ('warehouse_worker', 'Комірник'),
                             ('analyst', 'Аналітик'),
                             ('office_manager', 'Офіс менеджер'),
                             ('cleaner', 'Прибиральниця'),
                             ('other_position', 'Інше')
                         ])
    photo = FileField('Фотографія (тільки для керівних посад)', 
                     validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Тільки JPG, JPEG і PNG файли!')])
    submit = SubmitField('Додати користувача')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Користувач з таким ім\'ям вже існує.')

    def validate_phone_number(self, phone_number):
        if not phone_number.data.isdigit():
            raise ValidationError('Номер телефону повинен містити тільки цифри')
        if len(phone_number.data) != 9:
            raise ValidationError('Номер телефону повинен містити 9 цифр')

class LoginForm(FlaskForm):
    username = StringField('Логін', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Увійти')

class TestAssignmentForm(FlaskForm):
    material_id = SelectField('Матеріал', coerce=int, validators=[DataRequired()])
    start_date = DateTimeField('Дата початку', format='%Y-%m-%dT%H:%M', validators=[DataRequired()], render_kw={"lang": "uk"})
    end_date = DateTimeField('Дата закінчення', format='%Y-%m-%dT%H:%M', validators=[DataRequired()], render_kw={"lang": "uk"})
    submit = SubmitField('Призначити тест')

    def __init__(self, *args, **kwargs):
        super(TestAssignmentForm, self).__init__(*args, **kwargs)
        # Загружаем только материалы, у которых есть тесты
        materials_with_tests = Material.query.join(Test).order_by(Material.title).all()
        self.material_id.choices = [(m.id, m.title) for m in materials_with_tests]



    def validate_material_id(self, field):
        material = Material.query.get(field.data)
        if not material:
            raise ValidationError('Обраний матеріал не існує')
        
        # Проверяем, есть ли тест для этого материала
        test = Test.query.filter_by(material_id=material.id).first()
        if not test:
            raise ValidationError('Для цього матеріалу ще не створено тест')

    def validate_end_date(self, field):
        if field.data <= self.start_date.data:
            raise ValidationError('Дата закінчення повинна бути пізніше дати початку')

class EditUserForm(FlaskForm):
    username = StringField('Ім\'я користувача', validators=[DataRequired(), Length(min=2, max=50)])
    password = PasswordField('Новий пароль (залиште порожнім, щоб не змінювати)')
    confirm_password = PasswordField('Підтвердження нового паролю')
    phone_number = StringField('Номер телефону', 
                             validators=[DataRequired(), Length(min=9, max=9)],
                             render_kw={"placeholder": "Введіть 9 цифр"})
    role = SelectField('Доступ', 
                      choices=[
                          ('user', 'Користувач'),
                          ('admin', 'Адміністратор')
                      ],
                      validators=[DataRequired()])
    department = SelectField('Відділ',
                           choices=[
                               ('founders', 'Засновники компанії'),
                               ('general_director', 'Генеральний директор'),
                               ('accounting', 'Відділ Бухгалтерії'),
                               ('marketing', 'Відділ Маркетингу'),
                               ('online_sales', 'Відділ Онлайн продажу'),
                               ('offline_sales', 'Відділ Офлайн продажу'),
                               ('foreign_trade', 'Відділ ЗЕД'),
                               ('warehouse', 'Складський відділ'),
                               ('analytics', 'Відділ аналітики'),
                               ('other', 'Інше'),
                               ('abrams_production', 'Виробництво Abrams')
                           ],
                           validators=[DataRequired()])
    position = SelectField('Посада',
                         choices=[
                             ('founder', 'Засновник'),
                             ('general_director', 'Генеральний директор'),
                             ('department_head', 'Керівник відділу'),
                             ('accountant', 'Бухгалтер'),
                             ('photographer', 'Фотограф'),
                             ('marketer', 'Маркетолог'),
                             ('customer_manager', 'Менеджер по роботі з клієнтами'),
                             ('seller', 'Продавець'),
                             ('cashier', 'Касир'),
                             ('merchandiser', 'Мерчендайзер'),
                             ('foreign_trade_manager', 'Менеджер ЗЕД'),
                             ('warehouse_worker', 'Комірник'),
                             ('analyst', 'Аналітик'),
                             ('office_manager', 'Офіс менеджер'),
                             ('cleaner', 'Прибиральниця'),
                             ('other_position', 'Інше')
                         ])
    photo = FileField('Нова фотографія (тільки для керівних посад)', 
                     validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Тільки JPG, JPEG і PNG файли!')])
    submit = SubmitField('Оновити користувача')

    def __init__(self, original_username, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Користувач з таким ім\'ям вже існує.')

    def validate_phone_number(self, phone_number):
        if not phone_number.data.isdigit():
            raise ValidationError('Номер телефону повинен містити тільки цифри')
        if len(phone_number.data) != 9:
            raise ValidationError('Номер телефону повинен містити 9 цифр')

    def validate_password(self, password):
        # Если пароль указан, он должен быть не менее 6 символов
        if password.data and len(password.data) < 6:
            raise ValidationError('Пароль повинен містити не менше 6 символів')
    
    def validate_confirm_password(self, confirm_password):
        # Проверяем подтверждение пароля только если пароль был введен
        if self.password.data and confirm_password.data != self.password.data:
            raise ValidationError('Паролі повинні співпадати')

class EditTestAssignmentForm(FlaskForm):
    start_date = DateTimeField('Дата початку', format='%Y-%m-%dT%H:%M', validators=[DataRequired()], render_kw={"lang": "uk"})
    end_date = DateTimeField('Дата закінчення', format='%Y-%m-%dT%H:%M', validators=[DataRequired()], render_kw={"lang": "uk"})
    submit = SubmitField('Зберегти зміни')

    def validate_end_date(self, field):
        if field.data <= self.start_date.data:
            raise ValidationError('Дата закінчення повинна бути пізніше дати початку') 