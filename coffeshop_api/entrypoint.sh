#!/bin/bash
# Устанавливаем строгий режим
set -e

# Ожидание доступности базы данных
./wait-for-it.sh db:5432 -t 60 -- echo "PostgreSQL is ready"
# Применение миграций, если это необходимо
python manage.py makemigrations && python manage.py migrate

# Запуск вашего Django приложения
exec "$@"
