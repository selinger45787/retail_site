from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from models import User

class AddUserForm(FlaskForm):
    first_name = StringField('Ім\'я', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Прізвище', validators=[DataRequired(), Length(min=2, max=50)])
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

    def validate_username(self, first_name, last_name):
        username = f"{first_name.data} {last_name.data}"
        user = User.query.filter_by(username=username).first()
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