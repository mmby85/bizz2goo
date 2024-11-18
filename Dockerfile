#dockerfile for django app
FROM python:3.10-slim

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
        libatlas-base-dev gfortran supervisor \
        nano

        
WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

RUN python3 manage.py makemigrations

RUN python3 manage.py migrate

RUN python manage.py collectstatic --noinput

# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "myproject.wsgi:application"]
CMD ["gunicorn", "-c", "gunicorn_config.py", "myproject.wsgi:application"]

# CMD ["python", "manage.py", "runserver"]
