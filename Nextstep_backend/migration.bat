

REM Activate the virtual environment
call venv\Scripts\activate

REM Make migrations for any model changes
python manage.py makemigrations

REM Apply migrations to the database
python manage.py migrate

REM Start the development server
python manage.py runserver

REM Keep the window open
pause