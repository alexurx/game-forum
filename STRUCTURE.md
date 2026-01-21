# Структура проекта

Создайте следующую структуру папок и файлов:

```
game-forum/
│
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── forum_config.py
│   └── context_processors.py
│
├── users/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── migrations/
│       └── __init__.py
│
├── forum/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── migrations/
│       └── __init__.py
│
├── achievements/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── utils.py
│   └── migrations/
│       └── __init__.py
│
├── templates/
│   ├── base.html
│   ├── forum/
│   │   ├── index.html
│   │   ├── category_detail.html
│   │   ├── topic_detail.html
│   │   ├── create_topic.html
│   │   ├── edit_post.html
│   │   └── delete_post.html
│   ├── users/
│   │   ├── register.html
│   │   ├── login.html
│   │   ├── profile.html
│   │   ├── edit_profile.html
│   │   ├── password_reset_request.html
│   │   └── password_reset_confirm.html
│   └── achievements/
│       └── list.html
│
├── static/
│   └── (пусто - стили в base.html)
│
├── media/
│   └── avatars/
│       └── (загруженные аватары)
│
├── fixtures/
│   └── initial_data.json
│
├── manage.py
├── requirements.txt
├── README.md
├── .env
└── .gitignore
```

## Содержимое .env файла

```env
SECRET_KEY=django-insecure-change-me-in-production-12345
DEBUG=True
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## Содержимое .gitignore

```
*.pyc
__pycache__/
db.sqlite3
.env
media/
staticfiles/
venv/
.DS_Store
```

## Команды для создания структуры (Linux/Mac)

```bash
mkdir -p game-forum/{config,users,forum,achievements,templates/{forum,users,achievements},static,media/avatars,fixtures}
cd game-forum
touch config/{__init__.py,settings.py,urls.py,wsgi.py,forum_config.py,context_processors.py}
touch users/{__init__.py,admin.py,apps.py,models.py,views.py,forms.py,urls.py}
touch forum/{__init__.py,admin.py,apps.py,models.py,views.py,forms.py,urls.py}
touch achievements/{__init__.py,admin.py,apps.py,models.py,views.py,urls.py,utils.py}
touch manage.py requirements.txt README.md .env .gitignore
```

## Команды для создания структуры (Windows)

```cmd
mkdir game-forum\config game-forum\users game-forum\forum game-forum\achievements
mkdir game-forum\templates\forum game-forum\templates\users game-forum\templates\achievements
mkdir game-forum\static game-forum\media\avatars game-forum\fixtures
cd game-forum
type nul > manage.py
type nul > requirements.txt
type nul > README.md
type nul > .env
type nul > .gitignore
```

После создания структуры скопируйте содержимое из артефактов в соответствующие файлы.