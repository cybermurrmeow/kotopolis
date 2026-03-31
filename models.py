from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default='volunteer')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    email_confirmed = db.Column(db.Boolean, default=False)
    email_confirmed_at = db.Column(db.DateTime)
    security_question = db.Column(db.String(200))
    security_answer = db.Column(db.String(200))
    
    # НОВЫЕ ПОЛЯ ДЛЯ ПРОФИЛЯ
    bio = db.Column(db.Text)  # описание о себе
    
    def check_answer(self, answer):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.security_answer, answer) if self.security_answer else False


class Cat(db.Model):
    __tablename__ = 'cats'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    nickname = db.Column(db.String(100))
    age = db.Column(db.Integer)
    breed = db.Column(db.String(100))
    gender = db.Column(db.String(20))
    color = db.Column(db.String(50))
    weight = db.Column(db.Float)
    mood = db.Column(db.String(30))
    favorite_toy = db.Column(db.String(100))
    arrival_date = db.Column(db.Date, default=date.today)
    status = db.Column(db.String(50), default='В приюте')
    health = db.Column(db.Text)
    description = db.Column(db.Text)
    last_vacc_date = db.Column(db.Date, default=date.today)
    next_vacc_date = db.Column(db.Date)
    is_vaccinated = db.Column(db.Boolean, default=False)
    is_sterilized = db.Column(db.Boolean, default=False)
    photo_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    adoption_date = db.Column(db.Date)

    # Дополнительные поля
    personality = db.Column(db.Text)
    activity_level = db.Column(db.String(200))
    kids_friendly = db.Column(db.Boolean, default=True)
    cats_friendly = db.Column(db.Boolean, default=True)
    dogs_friendly = db.Column(db.Boolean, default=True)
    favorite_place = db.Column(db.String(200))
    vocal = db.Column(db.String(100))
    food_preferences = db.Column(db.Text)
    story = db.Column(db.Text)
    adoption_recommendation = db.Column(db.Text)
    
    @property
    def days_in_shelter(self):
        if self.arrival_date:
            if self.status == 'Усыновлён' and self.adoption_date:
                return (self.adoption_date - self.arrival_date).days
            return (date.today() - self.arrival_date).days
        return 0
    
    def vacc_status(self):
        if not self.last_vacc_date:
            return {'class': 'danger', 'text': '❌ Нет данных', 'icon': 'fa-times-circle'}
        today = date.today()
        days_since = (today - self.last_vacc_date).days
        if days_since > 365:
            return {'class': 'danger', 'text': '⚠️ Просрочена', 'icon': 'fa-exclamation-triangle'}
        elif days_since > 300:
            return {'class': 'warning', 'text': '⚡ Скоро просрочка', 'icon': 'fa-clock'}
        else:
            return {'class': 'success', 'text': '✅ Актуальна', 'icon': 'fa-check-circle'}
    
    def mood_emoji(self):
        return self.mood or 'Неизвестно'
    
    def validate_photo(self):
        if self.photo_path:
            if self.photo_path.startswith('http'):
                return True
            if not self.photo_path.lower().endswith('.gif'):
                raise ValueError('❌ Можно загружать только GIF-файлы!')
        return True
    
    def get_photo_type(self):
        if not self.photo_path:
            return None
        if self.photo_path.startswith('http'):
            return 'url'
        if self.photo_path.lower().endswith('.gif'):
            return 'gif'
        return 'image'


class AdoptionRequest(db.Model):
    __tablename__ = 'adoption_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    cat_id = db.Column(db.Integer, db.ForeignKey('cats.id'), nullable=False)
    
    # Исправленная связь с пользователем
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    user = db.relationship('User', backref='adoption_requests', lazy=True)
    
    adopter_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    comment = db.Column(db.Text)
    request_date = db.Column(db.Date, default=date.today)
    status = db.Column(db.String(50), default='На рассмотрении')
    
    cat = db.relationship('Cat', backref='adoption_requests')


class CatComment(db.Model):
    __tablename__ = 'cat_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    cat_id = db.Column(db.Integer, db.ForeignKey('cats.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('cat_comments.id', ondelete='CASCADE'), nullable=True)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    cat = db.relationship('Cat', backref='cat_comments')
    user = db.relationship('User', backref='user_comments')
    parent = db.relationship('CatComment', remote_side=[id], backref='replies')