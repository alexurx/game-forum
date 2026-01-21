# Быстрый старт

## Шаг 1: Создание проекта

```bash
# Создайте и перейдите в папку проекта
mkdir game-forum
cd game-forum

# Создайте виртуальное окружение
python -m venv venv

# Активируйте его
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

## Шаг 2: Установка Django

```bash
# Создайте файл requirements.txt со следующим содержимым
pip install Django==4.2.7
pip install Pillow==10.1.0
pip install python-decouple==3.8
pip install django-crispy-forms==2.1
pip install crispy-bootstrap4==2.0

# Или сохраните в requirements.txt и выполните:
pip install -r requirements.txt
```

## Шаг 3: Создание Django проекта

```bash
# Создайте Django проект
django-admin startproject config .

# Создайте приложения
python manage.py startapp users
python manage.py startapp forum
python manage.py startapp achievements
```

## Шаг 4: Копирование файлов

Скопируйте содержимое из артефактов в соответствующие файлы:

1. **config/settings.py** - настройки проекта
2. **config/urls.py** - главные URL
3. **config/forum_config.py** - конфигурация форума
4. **config/context_processors.py** - контекстный процессор
5. **users/models.py** - модели пользователей
6. **users/views.py** - views пользователей
7. **users/forms.py** - формы пользователей
8. **users/urls.py** - URL пользователей
9. **forum/models.py** - модели форума
10. **forum/views.py** - views форума
11. **forum/forms.py** - формы форума
12. **forum/urls.py** - URL форума
13. **achievements/models.py** - модели ачивок
14. **achievements/views.py** - views ачивок
15. **achievements/urls.py** - URL ачивок
16. **achievements/utils.py** - утилиты ачивок

## Шаг 5: Создание папки templates

```bash
mkdir -p templates/forum templates/users templates/achievements
mkdir -p media/avatars
mkdir fixtures
```

## Шаг 6: Копирование HTML шаблонов

Создайте и заполните следующие HTML файлы из артефактов:

- templates/base.html
- templates/forum/index.html
- templates/forum/category_detail.html
- templates/forum/topic_detail.html
- templates/forum/create_topic.html
- templates/forum/edit_post.html
- templates/forum/delete_post.html
- templates/users/register.html
- templates/users/login.html
- templates/users/profile.html
- templates/users/edit_profile.html
- templates/users/password_reset_request.html
- templates/users/password_reset_confirm.html
- templates/achievements/list.html

## Шаг 7: Копирование admin.py

Разделите содержимое из артефакта "Админ панель" на три файла:
- users/admin.py
- forum/admin.py
- achievements/admin.py

## Шаг 8: Создание .env файла

```env
SECRET_KEY=django-insecure-your-secret-key-here-change-in-production
DEBUG=True

# Email настройки для тестирования (письма будут выводиться в консоль)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@gameforum.local

# Для настоящей отправки email через Gmail используйте:
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-app-password
# DEFAULT_FROM_EMAIL=your-email@gmail.com
```

## Шаг 9: Создание начальных данных

Создайте файл `fixtures/initial_data.json` с содержимым из артефакта.

## Шаг 10: Миграции и запуск

```bash
# Создайте миграции
python manage.py makemigrations

# Примените миграции
python manage.py migrate

# Создайте суперпользователя
python manage.py createsuperuser

# Загрузите начальные данные
python manage.py loaddata fixtures/initial_data.json

# Запустите сервер
python manage.py runserver
```

## Готово!

Откройте браузер и перейдите на http://localhost:8000

## Тестовые данные

После создания суперпользователя:

1. Войдите в админку: http://localhost:8000/admin
2. Создайте несколько тестовых пользователей
3. Создайте несколько тем и сообщений
4. Проверьте систему ачивок

**Тестирование восстановления пароля:**
1. При использовании console backend письмо появится в терминале где запущен сервер
2. Скопируйте ссылку из письма и откройте в браузере
3. Установите новый пароль

## Настройка email (опционально)

**Для тестирования (по умолчанию):**
Email будет выводиться в консоль сервера. Просто используйте настройки из .env файла как есть.

**Для реальной отправки через Gmail:**
1. Включите двухфакторную аутентификацию в Google аккаунте
2. Создайте пароль приложения: https://myaccount.google.com/apppasswords
3. Обновите .env файл:
   ```env
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-16-char-app-password
   DEFAULT_FROM_EMAIL=your-email@gmail.com
   ```
4. Перезапустите сервер

**Для других почтовых сервисов:**
Измените EMAIL_HOST, EMAIL_PORT и другие параметры согласно документации вашего провайдера.

## Кастомизация

Отредактируйте `config/forum_config.py` для изменения:
- Названия форума
- Цветовой схемы
- Иконки
- Описания

## Возможные проблемы

**Ошибка импорта модулей:**
- Убедитесь, что все `__init__.py` файлы созданы
- Проверьте INSTALLED_APPS в settings.py

**Ошибка миграций:**
- Удалите папки migrations/* (кроме __init__.py)
- Выполните `python manage.py makemigrations` заново

**Ошибка статических файлов:**
- Выполните `python manage.py collectstatic`

**Ошибка отправки email:**
- Проверьте настройки в .env
- Для тестирования используйте console backend (по умолчанию):
  ```python
  EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
  ```
- Письма будут выводиться в консоль, а не отправляться на реальный email