FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y curl gnupg2 postgresql postgresql-contrib

RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get update && \
    apt-get install -y nodejs && \
    apt-get clean

WORKDIR /app
COPY . .


RUN pip install --upgrade pip
RUN pip install -r current_site/requirements.txt


WORKDIR /app/ExpressJS_service
RUN npm install

WORKDIR /app/current_site
RUN python manage.py collectstatic --noinput

WORKDIR /app
RUN pip install supervisor

COPY supervisord.conf /etc/supervisord.conf


COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 8000 3001

CMD ["/docker-entrypoint.sh"]
