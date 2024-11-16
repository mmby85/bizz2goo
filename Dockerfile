#dockerfile for django app
FROM python:3.6-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

RUN python3 manage.py makemigrations

RUN python3 manage.py migrate

# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "myproject.wsgi:application"]
CMD ["gunicorn", "-c", "gunicorn_config.py", "myproject.wsgi:application"]
