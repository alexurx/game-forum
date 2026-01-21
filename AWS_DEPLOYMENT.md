# Развертывание форума на AWS

Это руководство покажет, как развернуть Django форум на AWS EC2 с использованием Nginx и Gunicorn.

## Вариант 1: AWS EC2 (Рекомендуется для начинающих)

### Шаг 1: Создание EC2 инстанса

1. **Войдите в AWS Console**: https://console.aws.amazon.com/
2. **Перейдите в EC2**: Services → EC2
3. **Нажмите "Launch Instance"**

#### Настройки инстанса:
- **Name**: `forum-server`
- **AMI**: Ubuntu Server 22.04 LTS (Free tier eligible)
- **Instance type**: t2.micro (Free tier) или t2.small для лучшей производительности
- **Key pair**: Создайте новую или используйте существующую (скачайте .pem файл!)
- **Network settings**:
  - ✅ Allow SSH traffic from: My IP (для безопасности)
  - ✅ Allow HTTPS traffic from the internet
  - ✅ Allow HTTP traffic from the internet
- **Storage**: 8-20 GB (достаточно для начала)

4. **Нажмите "Launch Instance"**

### Шаг 2: Подключение к серверу

#### Для Windows (PowerShell):
```powershell
# Установите права на ключ (если используете WSL)
chmod 400 your-key.pem

# Подключитесь к серверу
ssh -i "your-key.pem" ubuntu@your-ec2-public-ip
```

#### Для Linux/Mac:
```bash
chmod 400 your-key.pem
ssh -i "your-key.pem" ubuntu@your-ec2-public-ip
```

### Шаг 3: Подготовка сервера

```bash
# Обновите систему
sudo apt update && sudo apt upgrade -y

# Установите необходимые пакеты
sudo apt install -y python3-pip python3-venv nginx postgresql postgresql-contrib

# Установите Git
sudo apt install -y git
```

### Шаг 4: Клонирование проекта

```bash
# Создайте директорию для проекта
cd /home/ubuntu
mkdir apps
cd apps

# Клонируйте ваш репозиторий (или загрузите файлы)
git clone <your-repo-url> forum
# ИЛИ создайте проект вручную и загрузите файлы через SCP/SFTP

cd forum
```

### Шаг 5: Настройка Python окружения

```bash
# Создайте виртуальное окружение
python3 -m venv venv

# Активируйте окружение
source venv/bin/activate

# Обновите pip
pip install --upgrade pip

# Установите зависимости
pip install -r requirements.txt

# Установите дополнительные production пакеты
pip install gunicorn psycopg2-binary
```

### Шаг 6: Настройка PostgreSQL (опционально, можно использовать SQLite)

```bash
# Войдите в PostgreSQL
sudo -u postgres psql

# Создайте базу данных и пользователя
CREATE DATABASE forum_db;
CREATE USER forum_user WITH PASSWORD 'secure_password_here';
ALTER ROLE forum_user SET client_encoding TO 'utf8';
ALTER ROLE forum_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE forum_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE forum_db TO forum_user;
\q
```

### Шаг 7: Настройка .env файла

```bash
# Создайте .env файл
nano .env
```

Добавьте следующее содержимое:
```env
SECRET_KEY=your-super-secret-key-generate-new-one
DEBUG=False
ALLOWED_HOSTS=your-domain.com,your-ec2-ip

# Database (если используете PostgreSQL)
# DATABASE_URL=postgresql://forum_user:secure_password_here@localhost/forum_db

# Email (для production)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

Сохраните: Ctrl+O, Enter, Ctrl+X

### Шаг 8: Обновите settings.py для production

Обновите `config/settings.py`:

```python
# В начале файла добавьте
import os
from pathlib import Path
from decouple import config, Csv

# ...

# Обновите ALLOWED_HOSTS
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# Для использования PostgreSQL (опционально)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'forum_db',
#         'USER': 'forum_user',
#         'PASSWORD': 'secure_password_here',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }

# Настройки безопасности для production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
```

### Шаг 9: Подготовка Django

```bash
# Активируйте виртуальное окружение (если не активно)
source venv/bin/activate

# Соберите статические файлы
python manage.py collectstatic --noinput

# Примените миграции
python manage.py migrate

# Создайте суперпользователя
python manage.py createsuperuser

# Загрузите начальные данные
python manage.py loaddata fixtures/initial_data.json
```

### Шаг 10: Настройка Gunicorn

Создайте systemd service файл:

```bash
sudo nano /etc/systemd/system/forum.service
```

Добавьте:
```ini
[Unit]
Description=Forum Gunicorn Daemon
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/apps/forum
Environment="PATH=/home/ubuntu/apps/forum/venv/bin"
ExecStart=/home/ubuntu/apps/forum/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/home/ubuntu/apps/forum/forum.sock \
    config.wsgi:application

[Install]
WantedBy=multi-user.target
```

Сохраните и запустите:
```bash
sudo systemctl start forum
sudo systemctl enable forum
sudo systemctl status forum
```

### Шаг 11: Настройка Nginx

```bash
sudo nano /etc/nginx/sites-available/forum
```

Добавьте:
```nginx
server {
    listen 80;
    server_name your-domain.com your-ec2-ip;

    client_max_body_size 10M;

    location = /favicon.ico { 
        access_log off; 
        log_not_found off; 
    }

    location /static/ {
        alias /home/ubuntu/apps/forum/staticfiles/;
    }

    location /media/ {
        alias /home/ubuntu/apps/forum/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/apps/forum/forum.sock;
    }
}
```

Активируйте конфигурацию:
```bash
sudo ln -s /etc/nginx/sites-available/forum /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Шаг 12: Настройка SSL (HTTPS) с Let's Encrypt

```bash
# Установите Certbot
sudo apt install -y certbot python3-certbot-nginx

# Получите SSL сертификат (замените на ваш домен)
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Автоматическое обновление сертификата
sudo systemctl status certbot.timer
```

### Шаг 13: Настройка файрвола

```bash
# Разрешите необходимые порты
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
sudo ufw status
```

## Вариант 2: AWS Elastic Beanstalk (Проще для деплоя)

### Требования:
```bash
pip install awsebcli
```

### Настройка:

1. **Создайте requirements.txt с production пакетами:**
```txt
Django==4.2.7
Pillow==10.1.0
python-decouple==3.8
django-crispy-forms==2.1
crispy-bootstrap4==2.0
gunicorn==21.2.0
psycopg2-binary==2.9.9
```

2. **Создайте .ebextensions/01_django.config:**
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: config.wsgi:application
  aws:elasticbeanstalk:environment:proxy:staticfiles:
    /static: staticfiles
```

3. **Инициализируйте Elastic Beanstalk:**
```bash
eb init -p python-3.11 forum-app --region us-east-1
eb create forum-env
eb deploy
```

## Обслуживание и мониторинг

### Просмотр логов:
```bash
# Django/Gunicorn логи
sudo journalctl -u forum -f

# Nginx логи
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Перезапуск сервисов:
```bash
# После изменений в коде
sudo systemctl restart forum

# После изменений в Nginx
sudo systemctl restart nginx
```

### Обновление кода:
```bash
cd /home/ubuntu/apps/forum
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart forum
```

## Безопасность

1. **Регулярно обновляйте систему:**
```bash
sudo apt update && sudo apt upgrade -y
```

2. **Настройте автоматические бэкапы базы данных:**
```bash
# Создайте скрипт бэкапа
nano ~/backup.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp /home/ubuntu/apps/forum/db.sqlite3 /home/ubuntu/backups/db_$DATE.sqlite3
# Удаляем старые бэкапы (старше 7 дней)
find /home/ubuntu/backups/ -name "db_*.sqlite3" -mtime +7 -delete
```

3. **Настройте мониторинг:**
- AWS CloudWatch для метрик
- Настройте алерты для высокой нагрузки

## Стоимость AWS

- **t2.micro** (Free tier): Бесплатно 750 часов/месяц первые 12 месяцев
- **t2.small**: ~$17/месяц
- **Elastic IP**: Бесплатно пока используется
- **Bandwidth**: Первые 100GB бесплатно

## Troubleshooting

### Ошибка 502 Bad Gateway:
```bash
# Проверьте статус Gunicorn
sudo systemctl status forum

# Проверьте права на sock файл
ls -l /home/ubuntu/apps/forum/forum.sock

# Перезапустите сервисы
sudo systemctl restart forum nginx
```

### Статические файлы не загружаются:
```bash
# Соберите заново
python manage.py collectstatic --noinput

# Проверьте права
sudo chown -R ubuntu:www-data /home/ubuntu/apps/forum/staticfiles
sudo chmod -R 755 /home/ubuntu/apps/forum/staticfiles
```

### База данных не подключается:
```bash
# Проверьте PostgreSQL
sudo systemctl status postgresql

# Проверьте настройки в .env
cat .env
```

## Полезные команды

```bash
# Статус всех сервисов
sudo systemctl status forum nginx postgresql

# Рестарт всего
sudo systemctl restart forum nginx

# Логи в реальном времени
sudo journalctl -u forum -f

# Проверка использования ресурсов
htop
df -h
free -m
```

## Дополнительно

- Настройте домен через Route 53
- Используйте AWS RDS для PostgreSQL вместо локальной БД
- Настройте S3 для хранения media файлов
- Используйте CloudFront для CDN
- Настройте автоматические бэкапы через AWS Backup

Готово! Ваш форум теперь работает на AWS! 🚀