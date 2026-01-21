#!/bin/bash

# Скрипт автоматического деплоя форума на Ubuntu 22.04
# Использование: bash deploy.sh

set -e  # Остановка при ошибке

echo "🚀 Начинаем развертывание форума на AWS EC2..."

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Проверка, что скрипт запущен на Ubuntu
if [ ! -f /etc/lsb-release ]; then
    echo -e "${RED}Ошибка: Этот скрипт предназначен для Ubuntu${NC}"
    exit 1
fi

# 1. Обновление системы
echo -e "${GREEN}[1/9] Обновление системы...${NC}"
sudo apt update -qq
sudo apt upgrade -y -qq

# 2. Установка зависимостей
echo -e "${GREEN}[2/9] Установка зависимостей...${NC}"
sudo apt install -y python3-pip python3-venv nginx git

# 3. Создание директории проекта
echo -e "${GREEN}[3/9] Создание директории проекта...${NC}"
cd /home/ubuntu
mkdir -p apps
cd apps

# Проверка, есть ли уже папка forum
if [ -d "forum" ]; then
    echo -e "${YELLOW}Папка forum уже существует. Пропускаем клонирование.${NC}"
    cd forum
else
    echo -e "${YELLOW}Скопируйте ваш проект в /home/ubuntu/apps/forum${NC}"
    echo -e "${YELLOW}Или используйте: git clone YOUR_REPO forum${NC}"
    exit 0
fi

# 4. Создание виртуального окружения
echo -e "${GREEN}[4/9] Настройка Python окружения...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# 5. Установка зависимостей Python
echo -e "${GREEN}[5/9] Установка Python пакетов...${NC}"
pip install --upgrade pip -q
pip install -r requirements.txt -q
pip install gunicorn -q

# 6. Проверка .env файла
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}[6/9] Создание .env файла...${NC}"
    
    # Генерация SECRET_KEY
    SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
    
    # Получение IP адреса
    EC2_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
    
    cat > .env << EOF
SECRET_KEY=${SECRET_KEY}
DEBUG=False
ALLOWED_HOSTS=${EC2_IP},localhost,127.0.0.1

# Email settings (console backend for testing)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@forum.local
EOF
    
    echo -e "${GREEN}✓ .env файл создан${NC}"
else
    echo -e "${GREEN}[6/9] .env файл уже существует${NC}"
fi

# 7. Подготовка Django
echo -e "${GREEN}[7/9] Подготовка Django...${NC}"
python manage.py collectstatic --noinput
python manage.py migrate

# Создание суперпользователя (интерактивно)
echo -e "${YELLOW}Создайте суперпользователя:${NC}"
python manage.py createsuperuser

# Загрузка начальных данных
if [ -f "fixtures/initial_data.json" ]; then
    python manage.py loaddata fixtures/initial_data.json
fi

# 8. Настройка Gunicorn
echo -e "${GREEN}[8/9] Настройка Gunicorn...${NC}"
sudo tee /etc/systemd/system/forum.service > /dev/null << EOF
[Unit]
Description=Forum Gunicorn Daemon
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/apps/forum
Environment="PATH=/home/ubuntu/apps/forum/venv/bin"
ExecStart=/home/ubuntu/apps/forum/venv/bin/gunicorn \\
    --workers 3 \\
    --bind unix:/home/ubuntu/apps/forum/forum.sock \\
    config.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl start forum
sudo systemctl enable forum

# 9. Настройка Nginx
echo -e "${GREEN}[9/9] Настройка Nginx...${NC}"

EC2_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)

sudo tee /etc/nginx/sites-available/forum > /dev/null << EOF
server {
    listen 80;
    server_name ${EC2_IP};
    
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
EOF

# Удаляем дефолтный конфиг и создаем symlink
sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/forum /etc/nginx/sites-enabled/

# Проверка конфигурации Nginx
sudo nginx -t

# Перезапуск Nginx
sudo systemctl restart nginx

# 10. Настройка firewall
echo -e "${GREEN}Настройка firewall...${NC}"
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
echo "y" | sudo ufw enable

# Готово!
echo -e "${GREEN}"
echo "=========================================="
echo "✅ Развертывание завершено успешно!"
echo "=========================================="
echo -e "${NC}"
echo ""
echo -e "${YELLOW}Ваш форум доступен по адресу:${NC}"
echo -e "${GREEN}http://${EC2_IP}${NC}"
echo ""
echo -e "${YELLOW}Админ-панель:${NC}"
echo -e "${GREEN}http://${EC2_IP}/admin/${NC}"
echo ""
echo -e "${YELLOW}Полезные команды:${NC}"
echo "  Просмотр логов:        sudo journalctl -u forum -f"
echo "  Перезапуск сервиса:    sudo systemctl restart forum"
echo "  Статус сервиса:        sudo systemctl status forum"
echo ""
echo -e "${YELLOW}Для настройки SSL (HTTPS):${NC}"
echo "  sudo apt install certbot python3-certbot-nginx"
echo "  sudo certbot --nginx -d your-domain.com"
echo ""