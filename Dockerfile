FROM python:3.11-slim

# Установим зависимости, PostgreSQL, curl, gnupg2
RUN apt-get update && \
    apt-get install -y curl gnupg2 postgresql postgresql-contrib

# Установим Node.js (LTS)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get update && \
    apt-get install -y nodejs && \
    apt-get clean

# Копируем проект
WORKDIR /app
COPY . .

# Python-зависимости
RUN pip install --upgrade pip
RUN pip install -r current_site/requirements.txt

# Node-зависимости
WORKDIR /app/ExpressJS_service
RUN npm install

# Собираем статику Django
WORKDIR /app/current_site
RUN python manage.py collectstatic --noinput

# Установим supervisor
WORKDIR /app
RUN pip install supervisor

# Копируем конфиг supervisor
COPY supervisord.conf /etc/supervisord.conf

# Копируем скрипт инициализации БД
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 8000 3001

CMD ["/docker-entrypoint.sh"]