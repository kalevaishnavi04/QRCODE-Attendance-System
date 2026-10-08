# 📱 QR Code Attendance System

A simple **QR Code-based Attendance Management System** built using **Django**.

Teachers can generate a QR code for a class and subject. Students scan the QR code and mark their attendance.

💻 **GitHub:**  
https://github.com/kalevaishnavi04/QRCODE-Attendance-System

---

## 🎯 Project Objective

This project helps teachers to:

- Reduce manual attendance work
- Generate QR codes for attendance
- Prevent duplicate attendance
- Use time-limited QR codes
- View attendance records
- Export attendance to Excel

---

## 🔄 How It Works

```text
Teacher Login
     ↓
Select Class & Subject
     ↓
Generate QR Code
     ↓
Student Scans QR
     ↓
Enter Name & Roll Number
     ↓
Student Validation
     ↓
Check Duplicate Attendance
     ↓
Attendance Recorded

⭐ Key Features
👨‍🏫 Teacher Login & Registration
📱 QR Code Attendance
⏱️ QR Code expires after 5 minutes
🚫 Duplicate attendance prevention
🏫 Class & Subject management
📊 Attendance statistics
📥 Excel attendance report
📱 Mobile QR scanning

🛠️ Technologies Used
Python
Django
SQLite
HTML
CSS
JavaScript
QR Code
OpenPyXL
Gunicorn
WhiteNoise
Render

📂 Project Structure
QRCODE-Attendance-System/
│
├── QR_code-Attendance-System-main/
│   └── attendance_system/
│       ├── attendance_system/
│       ├── core/
│       ├── manage.py
│       ├── requirements.txt
│       └── seed_demo.py
│
├── README.md
└── .gitignore

🚀 Installation

Clone the repository:

git clone https://github.com/kalevaishnavi04/QRCODE-Attendance-System.git

Go inside the project:

For your Django QR Attendance project, use these commands:

🖥️ Run locally
cd QR_code-Attendance-System-main
cd attendance_system

Activate virtual environment:
Windows:
venv\Scripts\activate

Install requirements:
python -m pip install -r requirements.txt

Run migrations:
python manage.py migrate

Run the project:
python manage.py runserver

Open in browser:
http://127.0.0.1:8000/

📱 For mobile QR testing
python manage.py runserver 0.0.0.0:8000

Then mobile browser:

http://YOUR-LAN-IP:8000/
🔮 Future Improvements
Student login
Admin dashboard
Better QR security
Attendance notifications
Monthly attendance reports
PDF reports
Better mobile UI

👩‍💻 Author

Vaishnavi Kale

B.E. Information Technology
Python Developer | Data Science & AI/ML Enthusiast

GitHub:
https://github.com/kalevaishnavi04

Portfolio:
https://kalevaishnavi04.github.io/vaishnavi-portfolio/

📄 Disclaimer

This project is developed for educational and portfolio purposes.
