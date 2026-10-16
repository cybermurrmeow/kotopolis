# Карта проекта

Здесь перечислены основные файлы и маршруты. За правилами доступа и валидацией нужно смотреть также `before_request` и формы.

## Основные модули

| Файл | Что находится внутри |
|---|---|
| app.py | Инициализация Flask/extensions, HTTP-маршруты, сессии, проверки ролей, письма |
| models.py | User, Cat, AdoptionRequest, FavoriteCat, CatComment и индексы |
| forms.py | Формы, типы и ограничения входных данных |
| media.py | Формат, бюджеты, пути и превью изображений |
| passwords.py | Единые правила допустимого пароля |
| utils.py | CSV/XLSX/PDF, формулы, статистика, шрифты |
| daily_story.py, story_bank.py | Выбор и редакционные тексты истории дня |
| manage.py | Демо-данные, CLI admin, rebuild previews |
| migrations/ | Baseline и три последующие ревизии |
| checks/ | Изолированные Chromium/PostgreSQL-проверки |
| tests/ | SQLite и unit/regression tests |
| templates/ | 24 Jinja-шаблона |
| static/css/ | Общие стили, страницы котиков, история дня и тёмная тема |
| static/js/ | Каталог, формы, профиль, избранное, прокрутка и тема |

## Все HTTP-маршруты

Гостю доступны только dashboard/cats/cat_details. Неподтверждённая почта и временный пароль ограничивают доступ через `before_request`. Все POST требуют CSRF. Flask также добавляет HEAD и OPTIONS к GET-маршрутам.

| Endpoint | URL | Методы | Основная защита |
|---|---|---|---|
| index | `/` | GET | публичный |
| register | `/register` | GET,POST | публичный, rate limit |
| confirm_email | `/confirm_email/<token>` | GET | публичный |
| verify_email_code | `/verify_email` | GET,POST | публичный, rate limit |
| resend_email_code | `/resend_email_code` | POST | публичный, rate limit |
| resend_confirmation | `/resend_confirmation` | GET,POST | публичный, rate limit |
| login | `/login` | GET,POST | публичный, rate limit |
| guest_login | `/guest_login` | POST | публичный |
| logout | `/logout` | POST | login |
| forgot_password | `/forgot_password` | GET,POST | публичный, rate limit |
| reset_password | `/reset_password/<token>` | GET,POST | публичный, rate limit |
| dashboard | `/dashboard` | GET | login |
| cats | `/cats` | GET | login |
| cat_details | `/cat/<int:cat_id>` | GET | login |
| add_cat | `/add_cat` | GET,POST | admin |
| edit_cat | `/edit_cat/<int:cat_id>` | GET,POST | admin |
| delete_cat | `/delete_cat/<int:cat_id>` | POST | admin |
| toggle_favorite | `/favorite/<int:cat_id>` | POST | login |
| favorites | `/favorites` | GET | login |
| create_adoption_request | `/cat/<int:cat_id>/adopt` | GET,POST | login |
| adoption_requests | `/adoption_requests` | GET | admin |
| update_adoption_request | `/adoption_request/<int:request_id>/status` | POST | admin |
| delete_adoption_request | `/adoption_request/<int:request_id>/delete` | POST | admin |
| profile | `/profile` | GET | login |
| users | `/users` | GET | admin |
| create_user | `/users/create` | POST | admin |
| update_user_role | `/user/<int:user_id>/role` | POST | admin |
| delete_user | `/user/<int:user_id>/delete` | POST | admin |
| exports_center | `/exports` | GET | admin |
| export_cats_csv | `/export_cats_csv` | GET | admin |
| export_cats_excel | `/export_cats_excel` | GET | admin |
| export_cats_pdf | `/export_cats_pdf` | GET | admin |
| edit_profile | `/edit_profile` | GET,POST | login |
| change_password | `/change_password` | GET,POST | login |
| cancel_my_request | `/cancel_my_request/<int:request_id>` | POST | login |
| toggle_favorite_cat | `/favorite_cat/<int:cat_id>` | POST | login |
| api_cats | `/api/cats` | GET | login |
| api_stats | `/api/stats` | GET | login |
| favicon | `/favicon.ico` | GET | публичный |

## Схема потоков

Запрос проходит CSRF и проверки доступа, затем маршрут проверяет форму и сохраняет изменения в БД. Ответом служит шаблон, перенаправление или файл экспорта. При загрузке изображения сначала проверяются поля и файл, затем создаются превью и запись сохраняется в БД. При ошибке новые файлы удаляются. Jinja экранирует HTML при выводе.

Старые маршруты сохранены: confirm_email перенаправляет к подтверждению почты, favorite_cat вызывает основную операцию избранного, delete_adoption_request не удаляет историю. Поля bio, security_question/security_answer и таблица cat_comments остаются в базе, но в интерфейсе не редактируются.

