# Карта проекта

Полная машинная карта финальной чистки прилагается отдельно: `kotopolis-cleanup-final-map.json`: исходники, размеры, импорты, маршруты с декораторами, точные CSS-дубли и JS без ссылок. Ниже карта актуального снимка.

## Основные модули

| Файл | Ответственность |
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
| static/css/ | 4 файла; порядок каскада сохранён |
| static/js/ | 8 подключаемых файлов |

## Все HTTP-маршруты

Доступ дополнительно ограничен before_request: гость читает только dashboard/cats/cat_details, неподтверждённый аккаунт теряет сессию, временный пароль блокирует рабочие страницы. Все POST требуют CSRF. GET включает обычные HEAD/OPTIONS Flask.

| Endpoint | URL | Методы | Основная защита | app.py, строка |
|---|---|---|---|---|
| index | `/` | GET | публичный | 696 |
| register | `/register` | GET,POST | публичный, rate limit | 708 |
| confirm_email | `/confirm_email/<token>` | GET | публичный | 791 |
| verify_email_code | `/verify_email` | GET,POST | публичный, rate limit | 805 |
| resend_email_code | `/resend_email_code` | POST | публичный, rate limit | 933 |
| resend_confirmation | `/resend_confirmation` | GET,POST | публичный, rate limit | 1017 |
| login | `/login` | GET,POST | публичный, rate limit | 1047 |
| guest_login | `/guest_login` | POST | публичный | 1143 |
| logout | `/logout` | POST | login | 1154 |
| forgot_password | `/forgot_password` | GET,POST | публичный, rate limit | 1166 |
| reset_password | `/reset_password/<token>` | GET,POST | публичный, rate limit | 1195 |
| dashboard | `/dashboard` | GET | login | 1262 |
| cats | `/cats` | GET | login | 1332 |
| cat_details | `/cat/<int:cat_id>` | GET | login | 1425 |
| add_cat | `/add_cat` | GET,POST | admin | 1540 |
| edit_cat | `/edit_cat/<int:cat_id>` | GET,POST | admin | 1593 |
| delete_cat | `/delete_cat/<int:cat_id>` | POST | admin | 1660 |
| toggle_favorite | `/favorite/<int:cat_id>` | POST | login | 1687 |
| favorites | `/favorites` | GET | login | 1734 |
| create_adoption_request | `/cat/<int:cat_id>/adopt` | GET,POST | login | 1747 |
| adoption_requests | `/adoption_requests` | GET | admin | 1840 |
| update_adoption_request | `/adoption_request/<int:request_id>/status` | POST | admin | 1855 |
| delete_adoption_request | `/adoption_request/<int:request_id>/delete` | POST | admin | 1947 |
| profile | `/profile` | GET | login | 1957 |
| users | `/users` | GET | admin | 1976 |
| create_user | `/users/create` | POST | admin | 1985 |
| update_user_role | `/user/<int:user_id>/role` | POST | admin | 2061 |
| delete_user | `/user/<int:user_id>/delete` | POST | admin | 2102 |
| exports_center | `/exports` | GET | admin | 2144 |
| export_cats_csv | `/export_cats_csv` | GET | admin | 2151 |
| export_cats_excel | `/export_cats_excel` | GET | admin | 2165 |
| export_cats_pdf | `/export_cats_pdf` | GET | admin | 2180 |
| edit_profile | `/edit_profile` | GET,POST | login | 2195 |
| change_password | `/change_password` | GET,POST | login | 2288 |
| cancel_my_request | `/cancel_my_request/<int:request_id>` | POST | login | 2340 |
| toggle_favorite_cat | `/favorite_cat/<int:cat_id>` | POST | login | 2369 |
| api_cats | `/api/cats` | GET | login | 2375 |
| api_stats | `/api/stats` | GET | login | 2437 |
| favicon | `/favicon.ico` | GET | публичный | 2478 |

## Схема потоков

Запрос -> CSRF/before_request -> route + role guard -> WTForms -> ORM transaction -> Jinja/redirect/export. Загрузка: form -> file validation -> preview budget -> file save -> ORM commit; при ошибке создаваемые файлы очищаются. HTML/Jinja output autoescape включён.

Сохранённые legacy URL: confirm_email перенаправляет к актуальному подтверждению, favorite_cat делегирует основной операции, delete_adoption_request отказывает в уничтожении истории. Данные bio, security_question/security_answer и cat_comments сохранены для совместимости; UI их не редактирует.

