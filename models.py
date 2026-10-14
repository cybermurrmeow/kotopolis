from datetime import UTC, date, datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


def utc_now():
    return datetime.now(UTC).replace(tzinfo=None)


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    __table_args__ = (
        db.Index("uq_users_username_lower", db.func.lower(username), unique=True),
    )
    # Email is not unique because historical production data may contain duplicates.
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="user")
    created_at = db.Column(db.DateTime, default=utc_now)
    last_login = db.Column(db.DateTime, nullable=True)
    email_confirmed = db.Column(db.Boolean, default=False)
    email_confirmed_at = db.Column(db.DateTime, nullable=True)
    must_change_password = db.Column(db.Boolean, nullable=False, default=False)
    email_code_hash = db.Column(db.String(255), nullable=True)
    email_code_expires_at = db.Column(db.DateTime, nullable=True)
    email_code_attempts = db.Column(db.Integer, nullable=False, default=0)
    email_code_sent_at = db.Column(db.DateTime, nullable=True)
    security_question = db.Column(db.String(200), nullable=True)
    security_answer = db.Column(db.String(200), nullable=True)
    # Kept for compatibility with existing accounts; it is not exposed in the UI.
    bio = db.Column(db.Text, nullable=True)
    adoption_requests = db.relationship(
        "AdoptionRequest", back_populates="user", passive_deletes="all", lazy=True
    )
    favorites = db.relationship(
        "FavoriteCat", back_populates="user", cascade="all, delete-orphan", lazy=True
    )
    comments = db.relationship(
        "CatComment", back_populates="user", passive_deletes="all", lazy=True
    )

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @property
    def is_admin(self):
        return self.role == "admin"

    def __repr__(self):
        return f"<User {self.username}>"


class Cat(db.Model):
    __tablename__ = "cats"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    nickname = db.Column(db.String(100), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    breed = db.Column(db.String(100), nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    color = db.Column(db.String(50), nullable=True)
    weight = db.Column(db.Float, nullable=True)
    mood = db.Column(db.String(30), nullable=True)
    favorite_toy = db.Column(db.String(100), nullable=True)
    arrival_date = db.Column(db.Date, nullable=True, default=date.today)
    status = db.Column(db.String(50), nullable=False, default="В приюте")
    health = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    last_vacc_date = db.Column(db.Date, nullable=True)
    next_vacc_date = db.Column(db.Date, nullable=True)
    is_vaccinated = db.Column(db.Boolean, default=False)
    is_sterilized = db.Column(db.Boolean, default=False)
    photo_path = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    adoption_date = db.Column(db.Date, nullable=True)
    previous_status = db.Column(db.String(50), nullable=True)
    shelter_days_frozen = db.Column(db.Integer, nullable=True)
    personality = db.Column(db.Text, nullable=True)
    activity_level = db.Column(db.String(200), nullable=True)
    kids_friendly = db.Column(db.Boolean, default=False)
    cats_friendly = db.Column(db.Boolean, default=False)
    dogs_friendly = db.Column(db.Boolean, default=False)
    favorite_place = db.Column(db.String(200), nullable=True)
    vocal = db.Column(db.String(100), nullable=True)
    food_preferences = db.Column(db.Text, nullable=True)
    story = db.Column(db.Text, nullable=True)
    adoption_recommendation = db.Column(db.Text, nullable=True)
    adoption_requests = db.relationship(
        "AdoptionRequest", back_populates="cat", passive_deletes="all", lazy=True
    )
    favorites = db.relationship(
        "FavoriteCat", back_populates="cat", cascade="all, delete-orphan", lazy=True
    )
    comments = db.relationship(
        "CatComment", back_populates="cat", passive_deletes="all", lazy=True
    )

    @property
    def days_in_shelter(self):
        if self.shelter_days_frozen is not None:
            return self.shelter_days_frozen

        if not self.arrival_date:
            return 0

        end_date = self.adoption_date or date.today()

        return max((end_date - self.arrival_date).days, 0)

    def age_category(self):
        if self.age is None:
            return "Возраст не указан"

        if self.age < 1:
            return "Котёнок"

        if self.age < 7:
            return "Взрослый"

        return "Пожилой"

    def vacc_status(self):
        if not self.is_vaccinated:
            return "Не вакцинирован"

        if self.next_vacc_date:
            if self.next_vacc_date < date.today():
                return "Вакцинация просрочена"

        return "Вакцинирован"

    def mood_emoji(self):
        moods = {
            "Весёлое": "😸",
            "Спокойное": "😌",
            "Игривое": "😺",
            "Грустное": "😿",
        }

        return moods.get(self.mood, "🐱")

    def __repr__(self):
        return f"<Cat {self.name}>"


class AdoptionRequest(db.Model):
    __tablename__ = "adoption_requests"
    __table_args__ = (
        db.Index(
            "uq_active_adoption_user_cat",
            "user_id",
            "cat_id",
            unique=True,
            postgresql_where=db.text(
                "user_id IS NOT NULL AND status IN ('Новая', 'На рассмотрении', 'Одобрена')"
            ),
            sqlite_where=db.text(
                "user_id IS NOT NULL AND status IN ('Новая', 'На рассмотрении', 'Одобрена')"
            ),
        ),
        db.Index(
            "uq_approved_adoption_cat",
            "cat_id",
            unique=True,
            postgresql_where=db.text("status = 'Одобрена'"),
            sqlite_where=db.text("status = 'Одобрена'"),
        ),
    )
    id = db.Column(db.Integer, primary_key=True)
    cat_id = db.Column(db.Integer, db.ForeignKey("cats.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    adopter_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=False)
    comment = db.Column(db.Text, nullable=True)
    request_date = db.Column(db.Date, default=date.today)
    status = db.Column(db.String(50), default="Новая")
    age = db.Column(db.Integer, nullable=True)
    occupation = db.Column(db.Text, nullable=True)
    housing = db.Column(db.Text, nullable=True)
    has_other_pets = db.Column(db.Boolean, default=False)
    experience = db.Column(db.Text, nullable=True)
    reason = db.Column(db.Text, nullable=True)
    cat = db.relationship("Cat", back_populates="adoption_requests")
    user = db.relationship("User", back_populates="adoption_requests")

    def __repr__(self):
        return f"<AdoptionRequest {self.id}>"


class FavoriteCat(db.Model):
    __tablename__ = "favorite_cats"
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    cat_id = db.Column(db.Integer, db.ForeignKey("cats.id"), primary_key=True)
    created_at = db.Column(db.DateTime, default=utc_now)
    user = db.relationship("User", back_populates="favorites")
    cat = db.relationship("Cat", back_populates="favorites")


class CatComment(db.Model):
    __tablename__ = "cat_comments"
    id = db.Column(db.Integer, primary_key=True)
    cat_id = db.Column(db.Integer, db.ForeignKey("cats.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("cat_comments.id"), nullable=True)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)
    cat = db.relationship("Cat", back_populates="comments")
    user = db.relationship("User", back_populates="comments")
    parent = db.relationship("CatComment", remote_side=[id], backref="replies")

    def __repr__(self):
        return f"<CatComment {self.id}>"
