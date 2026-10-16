from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed

from wtforms import (
    StringField,
    IntegerField,
    SelectField,
    SubmitField,
    DateField,
    FloatField,
    TextAreaField,
    BooleanField,
    PasswordField
)

from wtforms.validators import (
    DataRequired,
    Length,
    Optional,
    Email,
    EqualTo,
    Regexp,
    ValidationError,
    NumberRange
)

from models import User


# ==========================================================
# ФОРМА ВХОДА
# ==========================================================

class LoginForm(FlaskForm):

    username_or_email = StringField(
        'Логин или Email',
        validators=[
            DataRequired(
                message='Введите логин или email'
            ),
            Length(
                min=3,
                max=120,
                message='Должно быть от 3 до 120 символов'
            )
        ]
    )

    password = PasswordField(
        'Пароль',
        validators=[
            DataRequired(
                message='Пароль обязателен'
            ),
            Length(
                min=4,
                message='Пароль должен содержать минимум 4 символа'
            )
        ]
    )

    submit = SubmitField(
        'Войти в Котополис 🐱'
    )


# ==========================================================
# ФОРМА РЕГИСТРАЦИИ
# ==========================================================

class RegisterForm(FlaskForm):

    username = StringField(
        'Логин',
        validators=[
            DataRequired(
                message='Введите логин'
            ),
            Length(
                min=3,
                max=30,
                message='Логин должен быть от 3 до 30 символов'
            ),
            Regexp(
                r'^[a-zA-Z0-9_а-яА-ЯёЁ-]+$',
                message='Используйте только буквы, цифры, _ и -'
            )
        ]
    )

    email = StringField(
        'Email',
        validators=[
            DataRequired(
                message='Введите email'
            ),
            Email(
                message='Введите корректный email адрес'
            ),
            Length(
                max=120,
                message='Email не должен превышать 120 символов'
            )
        ]
    )

    password = PasswordField(
        'Пароль',
        validators=[
            DataRequired(
                message='Введите пароль'
            ),
            Length(
                min=8,
                max=128,
                message='Пароль должен быть от 8 до 128 символов'
            ),
            Regexp(
                r'^(?=.*[a-zA-Zа-яА-ЯёЁ])(?=.*\d).+$',
                message='Добавьте хотя бы одну букву и одну цифру'
            )
        ]
    )

    confirm_password = PasswordField(
        'Повторите пароль',
        validators=[
            DataRequired(
                message='Повторите пароль'
            ),
            EqualTo(
                'password',
                message='Пароли не совпадают'
            )
        ]
    )

    submit = SubmitField(
        'Создать аккаунт 🩷'
    )


# ==========================================================
# ФОРМА ДОБАВЛЕНИЯ / РЕДАКТИРОВАНИЯ КОТИКА
# ==========================================================

class CatForm(FlaskForm):

    name = StringField(
        'Имя',
        validators=[
            DataRequired(
                message='Имя обязательно'
            ),
            Length(
                max=100,
                message='Имя не должно превышать 100 символов'
            )
        ]
    )

    nickname = StringField(
        'Кличка / прозвище',
        validators=[
            Length(max=100)
        ]
    )

    age = IntegerField(
        'Возраст (лет)',
        validators=[
            Optional(),
            NumberRange(
                min=0,
                max=30,
                message='Возраст должен быть от 0 до 30 лет'
            )
        ]
    )

    breed = StringField(
        'Порода',
        validators=[
            Length(max=100)
        ]
    )

    gender = SelectField(
        'Пол',
        choices=[
            ('', 'Выберите пол'),
            ('Мальчик', 'Мальчик'),
            ('Девочка', 'Девочка')
        ]
    )

    color = StringField(
        'Окрас',
        validators=[
            Length(max=50)
        ]
    )

    weight = FloatField(
        'Вес (кг)',
        validators=[
            Optional(),
            NumberRange(
                min=0.2,
                max=30,
                message='Вес должен быть от 0.2 до 30 кг'
            )
        ]
    )

    mood = SelectField(
        'Настроение',
        choices=[
            ('', 'Выберите настроение'),
            ('Весёлое', 'Весёлое'),
            ('Спокойное', 'Спокойное'),
            ('Игривое', 'Игривое'),
            ('Грустное', 'Грустное'),
            ('Осторожное', 'Осторожное')
        ]
    )

    favorite_toy = StringField(
        'Любимая игрушка',
        validators=[
            Length(max=100)
        ]
    )

    arrival_date = DateField(
        'Дата поступления',
        format='%Y-%m-%d',
        validators=[
            Optional()
        ]
    )

    status = SelectField(
        'Статус',
        choices=[
            ('В приюте', 'В приюте'),
            ('Усыновлён', 'Усыновлён'),
            ('На лечении', 'На лечении'),
            ('В карантине', 'В карантине')
        ]
    )

    health = TextAreaField(
        'Состояние здоровья'
    )

    description = TextAreaField(
        'Подробное описание'
    )

    last_vacc_date = DateField(
        'Дата последней прививки',
        format='%Y-%m-%d',
        validators=[
            Optional()
        ]
    )

    next_vacc_date = DateField(
        'Дата следующей прививки',
        format='%Y-%m-%d',
        validators=[
            Optional()
        ]
    )

    adoption_date = DateField(
        'Дата усыновления',
        format='%Y-%m-%d',
        validators=[
            Optional()
        ]
    )

    is_vaccinated = BooleanField(
        'Вакцинирован'
    )

    is_sterilized = BooleanField(
        'Стерилизован / кастрирован'
    )

    photo = FileField(
        'Фото или GIF',
        validators=[
            FileAllowed(
                [
                    'jpg',
                    'jpeg',
                    'png',
                    'webp',
                    'gif'
                ],
                'Разрешены JPG, JPEG, PNG, WebP и GIF'
            )
        ]
    )

    personality = StringField(
        'Коротко о характере, для карточки',
        validators=[
            Optional(),
            Length(max=150)
        ]
    )

    activity_level = SelectField(
        'Активность',
        choices=[
            ('', 'Выберите уровень'),
            ('Высокий', 'Высокий'),
            ('Средний', 'Средний'),
            ('Низкий', 'Низкий')
        ],
        validators=[
            Optional()
        ]
    )

    kids_friendly = BooleanField(
        'Подходит для семей с детьми'
    )

    cats_friendly = BooleanField(
        'Ладит с другими кошками'
    )

    dogs_friendly = BooleanField(
        'Ладит с собаками'
    )

    favorite_place = StringField(
        'Любимое место',
        validators=[
            Optional(),
            Length(max=100)
        ]
    )

    food_preferences = StringField(
        'Особенности питания',
        validators=[
            Optional(),
            Length(max=200)
        ]
    )

    vocal = SelectField(
        'Голос',
        choices=[
            ('', 'Выберите'),
            ('Молчаливый', 'Молчаливый'),
            ('Разговорчивый', 'Разговорчивый'),
            ('Поющий', 'Поющий'),
            ('Мяукает редко', 'Мяукает редко')
        ],
        validators=[
            Optional()
        ]
    )

    story = TextAreaField(
        'Как кот попал в приют',
        validators=[
            Optional()
        ]
    )

    adoption_recommendation = TextAreaField(
        'Какая семья подойдёт',
        validators=[
            Optional()
        ]
    )

    gif_url = StringField(
        'Ссылка на изображение / GIF',
        validators=[
            Optional(),
            Length(
                max=200,
                message='Ссылка не должна превышать 200 символов'
            )
        ]
    )

    submit = SubmitField(
        'Сохранить котика'
    )


# ==========================================================
# ФОРМА ЗАЯВКИ НА УСЫНОВЛЕНИЕ
# Поздняя версия старого проекта
# ==========================================================

class AdoptionForm(FlaskForm):

    adopter_name = StringField(
        'Ваше имя',
        validators=[
            DataRequired(
                message='Имя обязательно'
            ),
            Length(
                min=2,
                max=100,
                message='Имя должно быть от 2 до 100 символов'
            ),
            Regexp(
                r'^[a-zA-Zа-яА-ЯёЁ\s\-]+$',
                message='Имя должно содержать только буквы, пробелы и дефис'
            )
        ]
    )

    age = IntegerField(
        'Возраст',
        validators=[
            DataRequired(
                message='Возраст обязателен'
            ),
            NumberRange(
                min=18,
                max=80,
                message='Возраст должен быть от 18 до 80 лет'
            )
        ]
    )

    phone = StringField(
        'Телефон',
        validators=[
            DataRequired(
                message='Телефон обязателен'
            ),
            Regexp(
                r'^\+?[0-9\-\s\(\)]{10,20}$',
                message='Введите корректный номер телефона'
            )
        ]
    )

    email = StringField(
        'Email',
        validators=[
            DataRequired(
                message='Email обязателен'
            ),
            Email(
                message='Введите корректный email адрес'
            ),
            Length(
                max=100,
                message='Email не должен превышать 100 символов'
            )
        ]
    )

    comment = TextAreaField(
        'Дополнительный комментарий',
        validators=[
            Optional(),
            Length(
                max=1000,
                message='Комментарий не должен превышать 1000 символов'
            )
        ]
    )

    submit = SubmitField(
        'Отправить заявку'
    )


# ==========================================================
# ФОРМА КОММЕНТАРИЯ
# ==========================================================

class CommentForm(FlaskForm):

    comment = TextAreaField(
        '💬 Ваш комментарий',
        validators=[
            DataRequired(
                message='Комментарий не может быть пустым'
            ),
            Length(
                max=500,
                message='Комментарий не должен превышать 500 символов'
            )
        ]
    )

    submit = SubmitField(
        '✍️ Добавить комментарий'
    )


# ==========================================================
# ВОССТАНОВЛЕНИЕ ПАРОЛЯ
# ==========================================================

class ForgotPasswordForm(FlaskForm):

    username = StringField(
        'Логин',
        validators=[
            DataRequired(
                message='Введите логин'
            ),
            Length(
                min=3,
                max=30,
                message='Логин должен быть от 3 до 30 символов'
            )
        ]
    )

    email = StringField(
        'Email',
        validators=[
            DataRequired(
                message='Введите email'
            ),
            Email(
                message='Введите корректный email'
            ),
            Length(
                max=120,
                message='Email не должен превышать 120 символов'
            )
        ]
    )

    submit = SubmitField(
        'Отправить ссылку'
    )


class ResetPasswordForm(FlaskForm):

    password = PasswordField(
        'Новый пароль',
        validators=[
            DataRequired(
                message='Введите новый пароль'
            ),
            Length(
                min=8,
                max=128,
                message='Пароль должен быть от 8 до 128 символов'
            ),
            Regexp(
                r'^(?=.*[a-zA-Zа-яА-ЯёЁ])(?=.*\d).+$',
                message='Добавьте хотя бы одну букву и одну цифру'
            )
        ]
    )

    confirm_password = PasswordField(
        'Повторите пароль',
        validators=[
            DataRequired(
                message='Повторите новый пароль'
            ),
            EqualTo(
                'password',
                message='Пароли не совпадают'
            )
        ]
    )

    submit = SubmitField(
        'Сохранить новый пароль'
    )


# ==========================================================
# ПОВТОРНАЯ ОТПРАВКА ПИСЬМА ПОДТВЕРЖДЕНИЯ
# ==========================================================

class ResendConfirmationForm(FlaskForm):

    username = StringField(
        'Логин',
        validators=[
            DataRequired(
                message='Введите логин'
            ),
            Length(
                min=3,
                max=30,
                message='Логин должен быть от 3 до 30 символов'
            )
        ]
    )

    email = StringField(
        'Email',
        validators=[
            DataRequired(
                message='Введите email'
            ),
            Email(
                message='Введите корректный email'
            ),
            Length(
                max=120,
                message='Email не должен превышать 120 символов'
            )
        ]
    )

    submit = SubmitField(
        'Отправить письмо ещё раз'
    )
