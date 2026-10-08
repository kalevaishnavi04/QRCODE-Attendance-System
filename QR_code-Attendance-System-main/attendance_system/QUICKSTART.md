# Quick start (Windows)

1. Zip extract kara.
2. `attendance_system` folder madhe `setup_and_run.bat` double-click kara
   (kinva manually: venv banva, `pip install -r requirements.txt`,
   `python manage.py migrate`, `python seed_demo.py`,
   `python manage.py runserver 0.0.0.0:8000`).
3. Browser: http://127.0.0.1:8000 -> Login (`teacher` / `teacher123`).
4. Dashboard -> Class-Year + Subject select -> Generate QR.
5. "Scan URL" ughda, roll number 1-5 taka -> Submit.

Phone var test: PC ani phone same Wi-Fi var; `ipconfig` madhun IPv4 ghya,
tya IP var (`http://<IP>:8000`) login karun QR generate kara.

Real data: http://127.0.0.1:8000/admin/ (Class years, Subjects, Students).
