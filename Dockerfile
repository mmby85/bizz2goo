#dockerfile for django app
FROM python:3.6-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

RUN python3 manage.py makemigrations

RUN python3 manage.py migrate

CMD python3 manage.py runserver 0.0.0.0:8000
