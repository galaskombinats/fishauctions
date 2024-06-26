@echo off
echo Starting Redis server...
start "Redis Server" cmd /k "redis-server

timeout /t 10

echo Starting Django server...
start "Django Server" cmd /k "cd /d C:\Users\ender\Desktop\DjangoWeb\fishauction && call fishauction_env\Scripts\activate && python manage.py runserver"

timeout /t 10

echo Starting Celery worker...
start "Celery Worker" cmd /k "cd /d C:\Users\ender\Desktop\DjangoWeb\fishauction && call fishauction_env\Scripts\activate && celery -A fishauction worker --loglevel=INFO --without-gossip --without-mingle --without-heartbeat -Ofair --pool=solo"

timeout /t 10

echo Starting Celery beat...
start "Celery Beat" cmd /k "cd /d C:\Users\ender\Desktop\DjangoWeb\fishauction && call fishauction_env\Scripts\activate && celery -A fishauction beat --loglevel=INFO"

echo All services started.
