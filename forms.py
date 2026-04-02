# ========== ИМПОРТЫ ==========
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, IntegerField, SelectField, SubmitField, 
    DateField, FloatField, TextAreaField, BooleanField, PasswordField
)
from wtforms.validators import (
    DataRequired, Length, Optional, Email, EqualTo, Regexp, ValidationError
)

# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
from models import User   # ← Оставляем, потому что используется для логина
# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←


# ========== КАСТОМНЫЕ ВАЛИДАТОРЫ ==========
def unique_username(form, field):
    username = field.data.strip().lower()
    if User.query.filter_by(username=username).first():
        raise ValidationError('Пользователь с таким логином уже существует')


# ========== ФОРМА ВХОДА ==========
class LoginForm(FlaskForm):
    username_or_email = StringField('Логин или Email', validators=[
        DataRequired(message='Введите логин или email'),
        Length(min=3, max=120, message='Должно быть от 3 до 120 символов')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Пароль обязателен'),
        Length(min=4, message='Пароль должен содержать минимум 4 символа')
    ])
    submit = SubmitField('Войти в Котополис 🐱')


# ========== ФОРМА РЕГИСТРАЦИИ ==========
class RegisterForm(FlaskForm):
    username = StringField('Логин', validators=[
        DataRequired(message='Логин обязателен'),
        Length(min=3, max=80, message='Логин должен быть от 3 до 80 символов'),
        Regexp(r'^[a-zA-Z0-9_а-яА-ЯёЁ\s]+$', message='Логин может содержать буквы, цифры и _'),
        unique_username          # ← Только проверка логина
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message='Email обязателен'),
        Email(message='Введите корректный email адрес'),
        Length(max=120, message='Email не должен превышать 120 символов')
        # unique_email — УБРАЛИ! Теперь можно регистрировать несколько аккаунтов на один email
    ])
    
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Пароль обязателен'),
        Length(min=4, max=100, message='Пароль должен быть от 4 до 100 символов'),
        Regexp(r'^(?=.*[a-zA-Z])(?=.*\d).+$', message='Пароль должен содержать хотя бы одну букву и одну цифру')
    ])
    
    confirm_password = PasswordField('Подтвердите пароль', validators=[
        DataRequired(message='Подтвердите пароль'),
        EqualTo('password', message='Пароли не совпадают')
    ])
    
    submit = SubmitField('Зарегистрироваться 🩷')


# ========== ФОРМА ДОБАВЛЕНИЯ КОТИКА ==========
class CatForm(FlaskForm):
    # Основные поля
    name = StringField('🐱 Имя', validators=[
        DataRequired(message='Имя обязательно'),
        Length(max=100, message='Имя не должно превышать 100 символов')
    ])
    nickname = StringField('🏷️ Кличка/прозвище', validators=[Length(max=100)])
    age = IntegerField('📅 Возраст (лет)', validators=[Optional()])
    breed = StringField('🐕 Порода', validators=[Length(max=100)])
    gender = SelectField('⚥ Пол', choices=[
        ('', 'Выберите пол'),
        ('Мальчик', 'Мальчик'),
        ('Девочка', 'Девочка')
    ])
    color = StringField('🎨 Окрас', validators=[Length(max=50)])
    weight = FloatField('⚖️ Вес (кг)', validators=[Optional()])
    mood = SelectField('😊 Настроение', choices=[
        ('', 'Выберите настроение'),
        ('Весёлое', 'Весёлое'),
        ('Спокойное', 'Спокойное'),
        ('Игривое', 'Игривое'),
        ('Грустное', 'Грустное')
    ])
    favorite_toy = StringField('🧸 Любимая игрушка', validators=[Length(max=100)])
    arrival_date = DateField('📆 Дата поступления', format='%Y-%m-%d', validators=[Optional()])
    status = SelectField('📌 Статус', choices=[
        ('В приюте', 'В приюте'),
        ('Усыновлён', 'Усыновлён'),
        ('На лечении', 'На лечении'),
        ('В карантине', 'В карантине')
    ])
    health = TextAreaField('💊 Состояние здоровья')
    description = TextAreaField('📝 Описание / Характер')
    last_vacc_date = DateField('💉 Дата последней прививки', format='%Y-%m-%d', validators=[Optional()])
    next_vacc_date = DateField('📅 Дата следующей прививки', format='%Y-%m-%d', validators=[Optional()])
    adoption_date = DateField('📅 Дата усыновления', format='%Y-%m-%d', validators=[Optional()])
    is_vaccinated = BooleanField('✅ Вакцинирован')
    is_sterilized = BooleanField('✂️ Стерилизован/кастрирован')
    photo = FileField('📸 Фото/GIF', validators=[
    FileAllowed(['gif'], 'Только GIF-файлы!')
])
    
    # Характер и поведение
    personality = SelectField('🐾 Характер', choices=[
        ('', 'Выберите характер'),
        ('Ласковый', 'Ласковый'),
        ('Игривый', 'Игривый'),
        ('Спокойный', 'Спокойный'),
        ('Независимый', 'Независимый'),
        ('Пугливый', 'Пугливый'),
        ('Энергичный', 'Энергичный'),
        ('Добрый', 'Добрый')
    ], validators=[Optional()])
    
    activity_level = SelectField('⚡ Активность', choices=[
        ('', 'Выберите уровень'),
        ('Высокий', 'Высокий'),
        ('Средний', 'Средний'),
        ('Низкий', 'Низкий')
    ], validators=[Optional()])
    
    kids_friendly = BooleanField('👶 Подходит для семей с детьми')
    cats_friendly = BooleanField('🐱 Ладит с другими кошками')
    dogs_friendly = BooleanField('🐕 Ладит с собаками')
    favorite_place = StringField('📍 Любимое место', validators=[Optional(), Length(max=100)])
    food_preferences = StringField('🍽️ Особенности питания', validators=[Optional(), Length(max=200)])
    
    vocal = SelectField('🎤 Голос', choices=[
        ('', 'Выберите'),
        ('Молчаливый', 'Молчаливый'),
        ('Разговорчивый', 'Разговорчивый'),
        ('Поющий', 'Поющий'),
        ('Мяукает редко', 'Мяукает редко')
    ], validators=[Optional()])
    
    story = TextAreaField('📖 История котика', validators=[Optional()])
    adoption_recommendation = TextAreaField('💡 Рекомендации для усыновителя', validators=[Optional()])
    gif_url = StringField('🔗 Или вставьте ссылку на GIF', validators=[Optional(), Length(max=500)])
    
    submit = SubmitField('💾 Сохранить котика')


# ========== ФОРМА УСЫНОВЛЕНИЯ ==========
class AdoptionForm(FlaskForm):
    adopter_name = StringField('👤 Ваше имя', validators=[
        DataRequired(message='Имя обязательно'),
        Length(max=100, message='Имя не должно превышать 100 символов')
    ])
    phone = StringField('📞 Телефон', validators=[Length(max=20)])
    email = StringField('📧 Email', validators=[
        DataRequired(message='Email обязателен'),
        Email(message='Введите корректный email адрес'),
        Length(max=100, message='Email не должен превышать 100 символов')
    ])
    comment = TextAreaField('💬 Комментарий', validators=[Length(max=500)])
    submit = SubmitField('📝 Отправить заявку на усыновление 🩷')


# ========== ФОРМА КОММЕНТАРИЯ ==========
class CommentForm(FlaskForm):
    comment = TextAreaField('💬 Ваш комментарий', validators=[
        DataRequired(message='Комментарий не может быть пустым'),
        Length(max=500, message='Комментарий не должен превышать 500 символов')
    ])
    submit = SubmitField('✍️ Добавить комментарий')


# ========== ФОРМА ВОССТАНОВЛЕНИЯ ПАРОЛЯ ==========
class ForgotPasswordForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(message='Логин обязателен')])
    security_answer = StringField('Ответ на контрольный вопрос', validators=[
        DataRequired(message='Ответ обязателен'),
        Length(min=2, message='Ответ должен содержать минимум 2 символа')
    ])
    new_password = PasswordField('Новый пароль', validators=[
        DataRequired(message='Пароль обязателен'),
        Length(min=4, message='Пароль должен содержать минимум 4 символа'),
        Regexp(r'^(?=.*[a-zA-Z])(?=.*\d).+$', message='Пароль должен содержать хотя бы одну букву и одну цифру')
    ])
    confirm_password = PasswordField('Подтвердите пароль', validators=[
        DataRequired(message='Подтвердите пароль'),
        EqualTo('new_password', message='Пароли не совпадают')
    ])
    submit = SubmitField('Восстановить пароль')


# ========== ФОРМА НАСТРОЙКИ КОНТРОЛЬНОГО ВОПРОСА ==========
class SetupSecurityForm(FlaskForm):
    security_question = SelectField('Контрольный вопрос', choices=[
        ('Кличка вашего первого питомца?', 'Кличка вашего первого питомца?'),
        ('Ваш любимый город?', 'Ваш любимый город?'),
        ('Имя вашей первой школы?', 'Имя вашей первой школы?'),
        ('Любимый цвет?', 'Любимый цвет?'),
        ('Имя вашего любимого кота?', 'Имя вашего любимого кота?')
    ], validators=[DataRequired()])
    security_answer = StringField('Ответ', validators=[
        DataRequired(message='Ответ обязателен'),
        Length(min=2, message='Ответ должен содержать минимум 2 символа')
    ])
    submit = SubmitField('Сохранить')