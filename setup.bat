@echo off
REM Windows Setup Script for LMS

echo.
echo ================================
echo LMS Project Setup Script
echo ================================
echo.

echo Setting up Python environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing dependencies...
pip install -r requirements.txt

echo Running migrations...
python manage.py makemigrations
python manage.py migrate

echo Creating superuser...
python manage.py createsuperuser

echo Collecting static files...
python manage.py collectstatic --noinput

echo.
echo ================================
echo Setup Complete!
echo ================================
echo.
echo To start the development server, run:
echo python manage.py runserver
echo.
echo Access points:
echo   Admin: http://localhost:8000/admin/
echo   API Docs: http://localhost:8000/api/docs/
echo.
pause
