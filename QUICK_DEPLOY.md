# Быстрый деплой на AWS EC2 - Чеклист

## 1️⃣ Создайте EC2 (5 минут)
- [ ] Создайте t2.micro Ubuntu 22.04 в AWS Console
- [ ] Скачайте .pem ключ
- [ ] Откройте порты: 22 (SSH), 80 (HTTP), 443 (HTTPS)
- [ ] Запишите Public IP адрес

## 2️⃣ Подключитесь к серверу (1 минута)
```bash
chmod 400 your-key.pem
ssh -i "your-key.pem" ubuntu@YOUR_EC2_IP
```

## 3️⃣ Установите все сразу (5 минут)
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv nginx git
```

## 4️⃣ Загрузите проект (2 минуты)
```bash
cd ~
mkdir apps && cd apps
git clone YOUR_REPO_URL forum
cd forum
```

## 5️⃣ Настройте Python (3 минуты)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

## 6️⃣ Создайте .env (1 минута)
```bash
nano .env
```
Вставьте:
```env
SECRET_KEY=generate-new-secret-key-here
DEBUG=False
ALLOWED_HOSTS=YOUR_EC2_IP,your-domain.com
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@forum.local
```

## 7️⃣ Подготовьте Django (2 минуты)
```bash
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py createsuperuser
python manage.py loaddata fixtures/initial_data.json
```

## 8️⃣ Gunicorn Service (2 минуты)
```bash
sudo nano /etc/systemd/system/forum.service
```
Вставьте:
```ini
[Unit]
Description=Forum Gunicorn
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/apps/forum
Environment="PATH=/home/ubuntu/apps/forum/venv/bin"
ExecStart=/home/ubuntu/apps/forum/venv/bin/gunicorn --workers 3 --bind unix:/home/ubuntu/apps/forum/forum.sock config.wsgi:application

[Install]
WantedBy=multi-user.target
```

Запустите:
```bash
sudo systemctl start forum
sudo systemctl enable forum
```

## 9️⃣ Nginx Config (2 минуты)
```bash
sudo nano /etc/nginx/sites-available/forum
```
Вставьте:
```nginx
server {
    listen 80;
    server_name YOUR_EC2_IP;
    
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

Активируйте:
```bash
sudo ln -s /etc/nginx/sites-available/forum /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔟 Готово! (0 минут)
Откройте в браузере: `http://YOUR_EC2_IP`

---

## ⚡ Для обновления кода:
```bash
cd /home/ubuntu/apps/forum
git pull
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart forum
```

## 🔍 Проверка логов:
```bash
sudo journalctl -u forum -f
sudo tail -f /var/log/nginx/error.log
```

## 🛡️ Добавить SSL (опционально):
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

**Общее время: ~25 минут** ⏱️