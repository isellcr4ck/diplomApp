#!/bin/bash
set -e

# Запуск PostgreSQL
service postgresql start

# Настройка БД (создание пользователя и базы, если не существует)
su postgres -c "psql -tc \"SELECT 1 FROM pg_roles WHERE rolname='currencio'\" | grep -q 1 || psql -c \"CREATE USER currencio WITH PASSWORD 'currencio';\""
su postgres -c "psql -tc \"SELECT 1 FROM pg_database WHERE datname='currencio'\" | grep -q 1 || psql -c \"CREATE DATABASE currencio OWNER currencio;\""

# Миграции Django
cd /app/current_site
python manage.py migrate

# Запуск supervisor (Express + Django)
exec /usr/local/bin/supervisord -c /etc/supervisord.conf