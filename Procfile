web: gunicorn greatbritishbeer.wsgi:application
release: python manage.py migrate && python manage.py collectstatic --noinput
