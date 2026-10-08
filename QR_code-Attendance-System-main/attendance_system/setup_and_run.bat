@echo off
REM Ek-click setup + run (Windows). manage.py asleli folder madhe double-click kara.
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python seed_demo.py
echo.
echo ================================================================
echo  Server suru hot ahe.
echo  Laptop var:  http://127.0.0.1:8000
echo  Phone var:   http://^<tumcha-PC-IPv4^>:8000   (ipconfig madhe bagha)
echo  Default login: teacher / teacher123  (jar adhi user nasel tar)
echo ================================================================
python manage.py runserver 0.0.0.0:8000
