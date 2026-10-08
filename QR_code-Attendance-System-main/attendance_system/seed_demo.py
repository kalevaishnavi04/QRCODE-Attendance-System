"""
Demo data bharto: Teacher login, Class Years, Subjects, Students.

Chalvaycha (manage.py asleli folder madhe, venv active astana):
    python seed_demo.py

Safe ahe: parat parat chalvla tari duplicate banvat nahi.
"""
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "attendance_system.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from core.models import ClassYear, Student, Subject  # noqa: E402

YEARS = ["FY", "SY", "TY"]
SUBJECTS = ["Python", "DBMS", "Maths"]
STUDENTS_PER_YEAR = 5

# Konihi user nasel tar default teacher banva (fakt local test sathi)
if not User.objects.exists():
    User.objects.create_superuser("teacher", "teacher@example.com", "teacher123")
    print("Default login banvla -> username: teacher   password: teacher123")

users = list(User.objects.all())

for year_name in YEARS:
    year, _ = ClassYear.objects.get_or_create(name=year_name)

    for subject_name in SUBJECTS:
        subject, _ = Subject.objects.get_or_create(name=subject_name, year=year)
        subject.teachers.add(*users)  # sagle users la teacher banvla

    for roll in range(1, STUDENTS_PER_YEAR + 1):
        Student.objects.get_or_create(
            roll_number=str(roll),
            class_year=year,
            defaults={"name": f"Student {year_name}-{roll}"},
        )

print("Done!")
print("Class years :", ClassYear.objects.count())
print("Subjects    :", Subject.objects.count())
print("Students    :", Student.objects.count())
print("Teachers    :", ", ".join(u.username for u in users))
print("Test sathi roll number 1 te", STUDENTS_PER_YEAR, "vapra.")
