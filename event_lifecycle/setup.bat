@echo off
echo === EventCert Setup ===
pip install -r requirements.txt
python manage.py migrate
python manage.py seed
echo.
echo === Creating superuser ===
python manage.py createsuperuser
echo.
echo === Starting server ===
python manage.py runserver
