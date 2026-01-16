web: gunicorn soggy_potatoes.wsgi --log-file -
release: python manage.py migrate --noinput && python manage.py collectstatic --noinput
