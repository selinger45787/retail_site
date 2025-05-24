from flask_wtf import FlaskForm
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
                               ('online', 'Онлайн відділ'),
                               ('offline', 'Офлайн відділ'),
                               ('office', 'Офіс'),
                               ('management', 'Відділ управління')
                           ],
                           validators=[DataRequired()])
    position = SelectField('Посада',
                         choices=[
                             ('seller', 'Продавець'),
                             ('cashier', 'Касир'),
                             ('manager', 'Менеджер офлайн відділу'),
                             ('merchandiser', 'Мерчендайзер'),
                             ('other', 'Інше')
                         ],
                         validators=[DataRequired()])
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
    user_id = SelectField('Сотрудник', coerce=int, validators=[DataRequired()])
    material_id = SelectField('Материал', coerce=int, validators=[DataRequired()])
    start_date = DateTimeField('Дата начала', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    end_date = DateTimeField('Дата окончания', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    submit = SubmitField('Назначить тест')

    def __init__(self, *args, **kwargs):
        super(TestAssignmentForm, self).__init__(*args, **kwargs)
        self.user_id.choices = [(u.id, u.username) for u in User.query.order_by(User.username).all()]
        self.material_id.choices = [(m.id, m.title) for m in Material.query.order_by(Material.title).all()]

    def validate_user_id(self, field):
        user = User.query.get(field.data)
        if not user:
            raise ValidationError('Выбранный сотрудник не существует')

    def validate_material_id(self, field):
        material = Material.query.get(field.data)
        if not material:
            raise ValidationError('Выбранный материал не существует')
        
        # Проверяем, есть ли тест для этого материала
        test = Test.query.filter_by(material_id=material.id).first()
        if not test:
            raise ValidationError('Для этого материала еще не создан тест')

    def validate_end_date(self, field):
        if field.data <= self.start_date.data:
            raise ValidationError('Дата окончания должна быть позже даты начала')

class EditTestAssignmentForm(FlaskForm):
    start_date = DateTimeField('Дата начала', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    end_date = DateTimeField('Дата окончания', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    submit = SubmitField('Сохранить изменения')

    def validate_end_date(self, field):
        if field.data <= self.start_date.data:
            raise ValidationError('Дата окончания должна быть позже даты начала') 