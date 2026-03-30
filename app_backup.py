import os
from datetime import date, datetime, timedelta
from io import BytesIO
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from models import db, User, Cat, AdoptionRequest, CatComment
from forms import LoginForm, RegisterForm, CatForm, AdoptionForm, CommentForm, ForgotPasswordForm, SetupSecurityForm
from utils import export_to_excel, generate_pdf_report, calculate_stats


# ====================== ДЕКОРАТОР ДЛЯ АДМИНА ======================
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Пожалуйста, войдите в систему', 'warning')
            return redirect(url_for('login'))
        if current_user.role != 'admin':
            flash('У вас нет прав для выполнения этого действия', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


# ====================== СОЗДАНИЕ ПРИЛОЖЕНИЯ ======================
app = Flask(__name__)
app.config['SECRET_KEY'] = 'kotopolis_pink_secret_key_2026_updated'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kotopolis.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Пожалуйста, войдите в систему для доступа к этой странице'
login_manager.login_message_category = 'warning'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ====================== ИНИЦИАЛИЗАЦИЯ БД И АДМИНА ======================
"""
# ====================== ИНИЦИАЛИЗАЦИЯ БД И АДМИНА ======================
with app.app_context():
    db.create_all()
    
    # Создаём админа если нет
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@kotopolis.ru',
            password=generate_password_hash('admin123', method='pbkdf2:sha256'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("=" * 50)
        print("✅ АДМИН СОЗДАН: admin / admin123")
        print("=" * 50)
    
    # Создаём волонтёра
    if not User.query.filter_by(username='volunteer').first():
        volunteer = User(
            username='volunteer',
            email='volunteer@kotopolis.ru',
            password=generate_password_hash('volunteer123', method='pbkdf2:sha256'),
            role='volunteer'
        )
        db.session.add(volunteer)
        db.session.commit()
        print("✅ Волонтёр создан: volunteer / volunteer123")
    
    # Добавляем тестовых котов если база пустая
    if Cat.query.count() == 0:
        test_cats = [
            Cat(name='Барсик', nickname='Барс', age=2, breed='Сиамский', gender='Mальчик',
                color='Кремовый', weight=4.5, mood='Игривое', favorite_toy='Мячик',
                status='В приюте', health='Здоров', description='Очень активный и ласковый кот',
                personality='Игривый', activity_level='Высокий', kids_friendly=True,
                cats_friendly=True, dogs_friendly=False, favorite_place='Окно',
                vocal='Разговорчивый', food_preferences='Сухой корм',
                story='Найден на улице в 2 месяца',
                adoption_recommendation='Идеальный кот для активной семьи'),
            Cat(name='Мурка', nickname='Мура', age=3, breed='Персидская', gender='Девочка',
                color='Белый', weight=3.8, mood='Спокойное', favorite_toy='Мышка',
                status='В приюте', health='Аллергия на корм', description='Спокойная и ласковая',
                personality='Ласковый', activity_level='Низкий', kids_friendly=True,
                cats_friendly=True, dogs_friendly=True, favorite_place='Диван',
                vocal='Молчаливый', food_preferences='Гипоаллергенный корм',
                story='Хозяйка переехала',
                adoption_recommendation='Идеальный компаньон для пожилых людей'),
            Cat(name='Рыжик', nickname='Рыжий', age=1, breed='Дворняжка', gender='Мальчик',
                color='Рыжий', weight=3.2, mood='Весёлое', favorite_toy='Верёвочка',
                status='В приюте', health='Здоров', description='Очень энергичный котёнок',
                personality='Игривый', activity_level='Высокий', kids_friendly=True,
                cats_friendly=True, dogs_friendly=True, favorite_place='Коробка',
                vocal='Разговорчивый', food_preferences='Влажный корм',
                story='Подкинули в приют',
                adoption_recommendation='Нужны активные игры')
        ]
        for cat in test_cats:
            db.session.add(cat)
        db.session.commit()
        print("✅ Добавлены тестовые коты")
"""


# ====================== МАРШРУТЫ ======================
@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/welcome')
@login_required
def welcome():
    return render_template('welcome.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.confirm_password.data:
            flash('Пароли не совпадают!', 'danger')
            return render_template('register.html', form=form)
        
        if User.query.filter_by(username=form.username.data).first():
            flash('Пользователь с таким логином уже существует', 'danger')
            return render_template('register.html', form=form)
        
        if form.email.data and User.query.filter_by(email=form.email.data).first():
            flash('Пользователь с таким email уже существует', 'danger')
            return render_template('register.html', form=form)
        
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data, method='pbkdf2:sha256'),
            role='volunteer'
        )
        db.session.add(new_user)
        db.session.commit()
        flash('🎉 Регистрация прошла успешно! Теперь вы можете войти в Котополис', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('welcome'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            user.last_login = datetime.utcnow()
            db.session.commit()
            login_user(user)
            flash(f'🐱 Добро пожаловать, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('welcome'))
        flash('❌ Неверный логин или пароль', 'danger')
    
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('👋 Вы вышли из системы', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    cats = Cat.query.all()
    stats = calculate_stats(cats)
    
    today = date.today()
    need_vacc = []
    for cat in cats:
        if not cat.last_vacc_date:
            need_vacc.append(cat)
        elif (today - cat.last_vacc_date).days > 365:
            need_vacc.append(cat)
    
    recent_cats = Cat.query.order_by(Cat.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         stats=stats,
                         need_vacc=need_vacc,
                         recent_cats=recent_cats,
                         cats=cats)  # <-- ДОБАВЬТЕ cats, если ещё нет


@app.route('/cats')
@login_required
def cats():
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    mood = request.args.get('mood', '')
    gender = request.args.get('gender', '')
    sort = request.args.get('sort', 'name')
    page = request.args.get('page', 1, type=int)
    per_page = 9
    
    query = Cat.query
    
    if search:
        query = query.filter(
            Cat.name.ilike(f'%{search}%') | 
            Cat.nickname.ilike(f'%{search}%') |
            Cat.breed.ilike(f'%{search}%')
        )
    if status:
        query = query.filter_by(status=status)
    if mood:
        query = query.filter_by(mood=mood)
    if gender:
        query = query.filter_by(gender=gender)
    
    if sort == 'age_asc':
        query = query.order_by(Cat.age)
    elif sort == 'age_desc':
        query = query.order_by(Cat.age.desc())
    elif sort == 'arrival_desc':
        query = query.order_by(Cat.arrival_date.desc())
    elif sort == 'arrival_asc':
        query = query.order_by(Cat.arrival_date)
    elif sort == 'name_desc':
        query = query.order_by(Cat.name.desc())
    else:
        query = query.order_by(Cat.name)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    all_statuses = ['В приюте', 'Усыновлён', 'На лечении', 'В карантине']
    all_moods = ['Весёлое', 'Спокойное', 'Игривое', 'Грустное']
    
    return render_template('cats.html', 
                         cats=pagination.items, 
                         pagination=pagination,
                         search=search, 
                         status=status, 
                         mood=mood,
                         gender=gender,
                         sort=sort,
                         all_statuses=all_statuses,
                         all_moods=all_moods)


@app.route('/cat/<int:cat_id>')
@login_required
def cat_details(cat_id):
    cat = Cat.query.get_or_404(cat_id)
    form = CommentForm()
    adoption_form = AdoptionForm()
    comments = CatComment.query.filter_by(cat_id=cat_id).order_by(CatComment.created_at.desc()).all()
    
    adoption_request = AdoptionRequest.query.filter_by(cat_id=cat_id, email=current_user.email).first()
    
    return render_template('cat_details.html', 
                         cat=cat, 
                         form=form, 
                         adoption_form=adoption_form,
                         comments=comments,
                         adoption_request=adoption_request)


@app.route('/add_cat', methods=['GET', 'POST'])
@login_required
@admin_required
def add_cat():
    form = CatForm()
    if form.validate_on_submit():
        photo_path = None
        
        # Приоритет: если есть ссылка на GIF, используем её
        if form.gif_url.data:
            photo_path = form.gif_url.data
        # Иначе загружаем файл
        elif form.photo.data:
            f = form.photo.data
            filename = secure_filename(f.filename)
            name_parts = filename.rsplit('.', 1)
            if len(name_parts) == 2:
                filename = f"{name_parts[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{name_parts[1]}"
            photo_path = f'uploads/{filename}'
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        new_cat = Cat(
            name=form.name.data,
            nickname=form.nickname.data,
            age=form.age.data,
            breed=form.breed.data,
            gender=form.gender.data,
            color=form.color.data,
            weight=form.weight.data,
            mood=form.mood.data,
            favorite_toy=form.favorite_toy.data,
            arrival_date=form.arrival_date.data or date.today(),
            status=form.status.data,
            health=form.health.data,
            description=form.description.data,
            last_vacc_date=form.last_vacc_date.data or date.today(),
            next_vacc_date=form.next_vacc_date.data,
            is_vaccinated=form.is_vaccinated.data,
            is_sterilized=form.is_sterilized.data,
            photo_path=photo_path,
            personality=form.personality.data,
            activity_level=form.activity_level.data,
            kids_friendly=form.kids_friendly.data,
            cats_friendly=form.cats_friendly.data,
            dogs_friendly=form.dogs_friendly.data,
            favorite_place=form.favorite_place.data,
            food_preferences=form.food_preferences.data,
            vocal=form.vocal.data,
            story=form.story.data,
            adoption_recommendation=form.adoption_recommendation.data
        )
        db.session.add(new_cat)
        db.session.commit()
        flash(f'🐱 Котик {new_cat.name} успешно добавлен в Котополис! 🩷', 'success')
        return redirect(url_for('cats'))
    
    return render_template('add_cat.html', form=form)


@app.route('/edit_cat/<int:cat_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_cat(cat_id):
    cat = Cat.query.get_or_404(cat_id)
    form = CatForm(obj=cat)
    
    if form.validate_on_submit():
        cat.name = form.name.data
        cat.nickname = form.nickname.data
        cat.age = form.age.data
        cat.breed = form.breed.data
        cat.gender = form.gender.data
        cat.color = form.color.data
        cat.weight = form.weight.data
        cat.mood = form.mood.data
        cat.favorite_toy = form.favorite_toy.data
        cat.arrival_date = form.arrival_date.data
        cat.status = form.status.data
        cat.health = form.health.data
        cat.description = form.description.data
        cat.last_vacc_date = form.last_vacc_date.data
        cat.next_vacc_date = form.next_vacc_date.data
        cat.is_vaccinated = form.is_vaccinated.data
        cat.is_sterilized = form.is_sterilized.data
        cat.personality = form.personality.data
        cat.activity_level = form.activity_level.data
        cat.kids_friendly = form.kids_friendly.data
        cat.cats_friendly = form.cats_friendly.data
        cat.dogs_friendly = form.dogs_friendly.data
        cat.favorite_place = form.favorite_place.data
        cat.food_preferences = form.food_preferences.data
        cat.vocal = form.vocal.data
        cat.story = form.story.data
        cat.adoption_recommendation = form.adoption_recommendation.data
        
        # Обновляем фото/гиф
        if form.gif_url.data:
            cat.photo_path = form.gif_url.data
        elif form.photo.data:
            f = form.photo.data
            filename = secure_filename(f.filename)
            name_parts = filename.rsplit('.', 1)
            if len(name_parts) == 2:
                filename = f"{name_parts[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{name_parts[1]}"
            photo_path = f'uploads/{filename}'
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cat.photo_path = photo_path
        
        cat.updated_at = datetime.utcnow()
        db.session.commit()
        flash(f'✅ Данные котика {cat.name} обновлены!', 'success')
        return redirect(url_for('cat_details', cat_id=cat.id))
    
    return render_template('edit_cat.html', form=form, cat=cat)


@app.route('/delete_cat/<int:cat_id>')
@login_required
@admin_required
def delete_cat(cat_id):
    cat = Cat.query.get_or_404(cat_id)
    cat_name = cat.name
    
    if cat.photo_path:
        try:
            photo_full_path = os.path.join('static', cat.photo_path)
            if os.path.exists(photo_full_path):
                os.remove(photo_full_path)
        except Exception as e:
            print(f"Ошибка при удалении фото: {e}")
    
    db.session.delete(cat)
    db.session.commit()
    flash(f'🗑️ Котик {cat_name} удалён из базы', 'warning')
    return redirect(url_for('cats'))


@app.route('/add_comment/<int:cat_id>', methods=['POST'])
@login_required
def add_comment(cat_id):
    cat = Cat.query.get_or_404(cat_id)
    form = CommentForm()
    
    if form.validate_on_submit():
        comment = CatComment(
            cat_id=cat_id,
            user_id=current_user.id,
            comment=form.comment.data
        )
        db.session.add(comment)
        db.session.commit()
        flash('💬 Комментарий добавлен!', 'success')
    
    return redirect(url_for('cat_details', cat_id=cat_id))


@app.route('/adopt/<int:cat_id>', methods=['GET', 'POST'])
@login_required
def adopt(cat_id):
    cat = Cat.query.get_or_404(cat_id)
    
    if cat.status == 'Усыновлён':
        flash('❌ Этот котик уже усыновлён!', 'warning')
        return redirect(url_for('cat_details', cat_id=cat_id))
    
    form = AdoptionForm()
    
    if form.validate_on_submit():
        existing = AdoptionRequest.query.filter_by(
            cat_id=cat_id, 
            email=form.email.data
        ).first()
        
        if existing:
            flash('📝 Вы уже подавали заявку на этого котика! Мы свяжемся с вами.', 'info')
            return redirect(url_for('cat_details', cat_id=cat_id))
        
        adoption_request = AdoptionRequest(
            cat_id=cat_id,
            adopter_name=form.adopter_name.data,
            phone=form.phone.data,
            email=form.email.data,
            comment=form.comment.data
        )
        db.session.add(adoption_request)
        db.session.commit()
        
        flash(f'🩷 Спасибо! Заявка на усыновление {cat.name} отправлена. Мы свяжемся с вами в ближайшее время!', 'success')
        return redirect(url_for('cat_details', cat_id=cat_id))
    
    return render_template('adopt.html', form=form, cat=cat)


@app.route('/export_excel')
@login_required
def export_excel():
    cats = Cat.query.all()
    excel_file = export_to_excel(cats)
    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'kotopolis_report_{date.today()}.xlsx'
    )


@app.route('/report')
@login_required
def report():
    cats = Cat.query.all()
    pdf_file = generate_pdf_report(cats, f"Отчёт Котополис от {date.today()}")
    return send_file(
        pdf_file,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'kotopolis_report_{date.today()}.pdf'
    )


@app.route('/api/cats')
@login_required
def api_cats():
    cats = Cat.query.all()
    return jsonify([{
        'id': cat.id,
        'name': cat.name,
        'age': cat.age,
        'breed': cat.breed,
        'status': cat.status,
        'mood': cat.mood,
        'photo': cat.photo_path
    } for cat in cats])


@app.route('/api/stats')
@login_required
def api_stats():
    cats = Cat.query.all()
    stats = calculate_stats(cats)
    return jsonify(stats)


@app.route('/adoption_requests')
@login_required
def adoption_requests():
    if current_user.role != 'admin':
        flash('У вас нет прав для просмотра этой страницы', 'danger')
        return redirect(url_for('dashboard'))
    
    status_filter = request.args.get('status_filter', '')
    search_query = request.args.get('search', '')
    
    query = AdoptionRequest.query
    
    if status_filter and status_filter != '':
        query = query.filter(AdoptionRequest.status == status_filter)
    
    if search_query and search_query != '':
        query = query.join(Cat).filter(
            db.or_(
                AdoptionRequest.adopter_name.ilike(f'%{search_query}%'),
                Cat.name.ilike(f'%{search_query}%'),
                Cat.nickname.ilike(f'%{search_query}%')
            )
        )
    
    requests = query.order_by(AdoptionRequest.request_date.desc()).all()
    
    return render_template(
        'adoption_requests.html', 
        requests=requests,
        current_status_filter=status_filter,
        current_search=search_query
    )


@app.route('/update_request_status/<int:request_id>', methods=['POST'])
@login_required
def update_request_status(request_id):
    if current_user.role != 'admin':
        flash('У вас нет прав для этого действия', 'danger')
        return redirect(url_for('dashboard'))
    
    request_item = AdoptionRequest.query.get_or_404(request_id)
    new_status = request.form.get('status')
    
    if new_status in ['На рассмотрении', 'Одобрена', 'Отклонена', 'Завершена']:
        request_item.status = new_status
        db.session.commit()
        flash(f'Статус заявки изменён на "{new_status}"', 'success')
    
    return redirect(url_for('adoption_requests'))


@app.route('/delete_request/<int:request_id>')
@login_required
def delete_request(request_id):
    if current_user.role != 'admin':
        flash('Только администратор может удалять заявки', 'danger')
        return redirect(url_for('dashboard'))
    
    request_item = AdoptionRequest.query.get_or_404(request_id)
    db.session.delete(request_item)
    db.session.commit()
    flash('Заявка удалена', 'success')
    
    return redirect(url_for('adoption_requests'))


# ====================== ВОССТАНОВЛЕНИЕ ПАРОЛЯ ======================
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    user_question = None
    user_exists = False
    
    if request.method == 'POST':
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_answer(form.security_answer.data):
            new_password = form.new_password.data
            old_password = user.password
            
            # Проверяем, что новый пароль не совпадает со старым
            if check_password_hash(old_password, new_password):
                flash('Новый пароль не должен совпадать со старым!', 'danger')
                return redirect(url_for('forgot_password', username=form.username.data))
            
            # Проверяем длину пароля
            if len(new_password) < 4:
                flash('Пароль должен содержать минимум 4 символа', 'danger')
                return redirect(url_for('forgot_password', username=form.username.data))
            
            # Проверяем, что пароли совпадают
            if new_password != form.confirm_password.data:
                flash('Пароли не совпадают', 'danger')
                return redirect(url_for('forgot_password', username=form.username.data))
            
            # Обновляем пароль
            user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
            db.session.commit()
            flash('Пароль успешно изменён! Теперь вы можете войти с новым паролем.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Неверный логин или ответ на контрольный вопрос', 'danger')
    
    # Получаем вопрос пользователя, если логин указан в GET параметре
    username = request.args.get('username')
    if username:
        user = User.query.filter_by(username=username).first()
        if user:
            user_question = user.security_question
            user_exists = True
    
    return render_template('forgot_password.html', 
                         form=form, 
                         user_question=user_question,
                         user_exists=user_exists)


@app.route('/setup_security/<int:user_id>', methods=['GET', 'POST'])
@login_required
def setup_security(user_id):
    # Проверяем, что пользователь настраивает свой профиль
    if user_id != current_user.id:
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('dashboard'))
    
    from forms import SetupSecurityForm
    form = SetupSecurityForm()
    
    if form.validate_on_submit():
        # Сохраняем контрольный вопрос и ответ
        current_user.security_question = form.security_question.data
        current_user.security_answer = generate_password_hash(form.security_answer.data)  # Храним в хешированном виде
        db.session.commit()
        flash('Контрольный вопрос успешно настроен!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('setup_security.html', form=form)


@app.route('/get_security_question')
def get_security_question():
    username = request.args.get('username')
    user = User.query.filter_by(username=username).first()
    if user and user.security_question:
        return jsonify({'question': user.security_question})
    return jsonify({'question': None})


# ====================== ОБРАБОТЧИКИ ОШИБОК ======================
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)