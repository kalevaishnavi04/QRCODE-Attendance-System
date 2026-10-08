import base64
import io
import logging
import os
import socket
import uuid
from collections import defaultdict
from datetime import timedelta

import qrcode

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from openpyxl import Workbook

from .forms import SimpleRegisterForm
from .models import (
    AttendanceRecord,
    AttendanceSession,
    ClassYear,
    Student,
    Subject,
)
from .utils import is_session_expired


# How long a QR code stays valid (minutes)
QR_EXPIRY_MINUTES = 5

logger = logging.getLogger(__name__)


# ============================================================
# GET LAPTOP LAN IP
# ============================================================

def get_lan_ip():
    """
    Laptop cha Wi-Fi/LAN IP.
    Example: 10.69.232.1
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]

    except OSError:
        return "127.0.0.1"

    finally:
        s.close()


# ============================================================
# BUILD QR SCAN URL
# ============================================================

def build_scan_url(request, token):
    """
    QR madhye student attendance mark karaycha URL create karto.

    Localhost / 127.0.0.1 / 0.0.0.0 asel tar
    laptop cha LAN IP use karto.

    Example:
    http://10.69.232.1:8000/student/mark/<token>/
    """

    path = f"/student/mark/{token}/"

    base = os.environ.get("PUBLIC_BASE_URL")

    if base:
        return base.rstrip("/") + path

    host = request.get_host()

    hostname, _, port = host.partition(":")

    if hostname in ("localhost", "127.0.0.1", "0.0.0.0"):
        lan_ip = get_lan_ip()

        if port:
            host = f"{lan_ip}:{port}"
        else:
            host = lan_ip

    return f"{request.scheme}://{host}{path}"


# ============================================================
# HOME
# ============================================================

def home(request):
    return render(request, "core/home.html")


# ============================================================
# REGISTER
# ============================================================

def register_view(request):

    if request.method == "POST":

        form = SimpleRegisterForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Registered successfully! Please log in."
            )

            return redirect("login")

    else:
        form = SimpleRegisterForm()

    return render(
        request,
        "core/register.html",
        {"form": form}
    )


# ============================================================
# LOGIN
# ============================================================

def login_view(request):

    if request.method == "POST":

        form = AuthenticationForm(
            request,
            data=request.POST
        )

        if form.is_valid():

            user = form.get_user()

            login(request, user)

            return redirect("dashboard")

        else:

            messages.error(
                request,
                "Invalid credentials"
            )

    else:
        form = AuthenticationForm()

    return render(
        request,
        "core/login.html",
        {"form": form}
    )


# ============================================================
# LOGOUT
# ============================================================

def logout_view(request):

    logout(request)

    return redirect("login")


# ============================================================
# TEACHER DASHBOARD
# ============================================================

@login_required
def teacher_dashboard(request):

    years = ClassYear.objects.all()

    subjects = Subject.objects.all()

    today = timezone.localdate()

    # --------------------------------------------------------
    # Filter values
    # --------------------------------------------------------

    selected_class_year_id = request.GET.get("class_year")

    selected_subject_id = request.GET.get("subject")

    selected_class_year = None

    selected_subject = None

    # --------------------------------------------------------
    # Get selected class year
    # --------------------------------------------------------

    if selected_class_year_id:

        try:

            selected_class_year = ClassYear.objects.get(
                id=selected_class_year_id
            )

        except (
            ClassYear.DoesNotExist,
            ValueError
        ):

            selected_class_year = None

    # --------------------------------------------------------
    # Get selected subject
    # --------------------------------------------------------

    if selected_subject_id:

        try:

            selected_subject = Subject.objects.get(
                id=selected_subject_id
            )

        except (
            Subject.DoesNotExist,
            ValueError
        ):

            selected_subject = None

    # --------------------------------------------------------
    # Filter students
    # --------------------------------------------------------

    students_qs = Student.objects.all()

    if selected_class_year:

        students_qs = students_qs.filter(
            class_year=selected_class_year
        )

    total_students = students_qs.count()

    # --------------------------------------------------------
    # Today's sessions
    # --------------------------------------------------------

    sessions_today = AttendanceSession.objects.filter(
        teacher=request.user,
        date=today
    )

    if selected_class_year:

        sessions_today = sessions_today.filter(
            class_year=selected_class_year
        )

    if selected_subject:

        sessions_today = sessions_today.filter(
            subject=selected_subject
        )

    # --------------------------------------------------------
    # Attendance statistics
    # --------------------------------------------------------

    present_today = AttendanceRecord.objects.filter(
        session__in=sessions_today
    ).count()

    attendance_percent = (
        round(
            (present_today / total_students) * 100,
            2
        )
        if total_students
        else 0
    )

    # --------------------------------------------------------
    # Attendance Records Table
    # --------------------------------------------------------

    if selected_class_year:

        attendance_sessions = AttendanceSession.objects.filter(
            teacher=request.user,
            class_year=selected_class_year
        )

    else:

        attendance_sessions = AttendanceSession.objects.filter(
            teacher=request.user
        )

    attendance_records = []

    for session in attendance_sessions:

        total_students_for_session = Student.objects.filter(
            class_year=session.class_year
        ).count()

        present_count = AttendanceRecord.objects.filter(
            session=session
        ).count()

        absent_count = (
            total_students_for_session
            - present_count
        )

        attendance_records.append(
            {
                "date": session.date,
                "subject": session.subject.name,
                "class_year": session.class_year.name,
                "present_count": present_count,
                "absent_count": absent_count,
            }
        )

    # --------------------------------------------------------
    # Today's present students
    # --------------------------------------------------------

    student_attendance_map = defaultdict(list)

    present_students_today = []

    for session in sessions_today:

        records = (
            AttendanceRecord.objects
            .filter(session=session)
            .select_related("student")
        )

        for record in records:

            row = {
                "name": record.student.name,
                "roll": record.student.roll_number,
                "subject": session.subject.name,
                "class": session.class_year.name,
                "time": timezone.localtime(
                    record.timestamp
                ).strftime("%I:%M:%S %p"),
            }

            student_attendance_map[
                session.id
            ].append(row)

            present_students_today.append(row)

    # --------------------------------------------------------
    # Render dashboard
    # --------------------------------------------------------

    return render(
        request,
        "core/dashboard.html",
        {
            "years": years,
            "subjects": subjects,
            "today": today,
            "total_students": total_students,
            "present_today": present_today,
            "attendance_percent": attendance_percent,
            "attendance_records": attendance_records,
            "selected_class_year": (
                selected_class_year.id
                if selected_class_year
                else ""
            ),
            "selected_subject_id": (
                selected_subject.id
                if selected_subject
                else ""
            ),
            "student_attendance_map": student_attendance_map,
            "present_students_today": present_students_today,
        }
    )


# ============================================================
# GET STATISTICS
# ============================================================

@login_required
def get_statistics(request):

    today = timezone.localdate()

    class_year_id = request.GET.get("class_year")

    subject_id = request.GET.get("subject")

    students = Student.objects.all()

    sessions_today = AttendanceSession.objects.filter(
        teacher=request.user,
        date=today
    )

    if class_year_id and class_year_id.isdigit():

        students = students.filter(
            class_year_id=class_year_id
        )

        sessions_today = sessions_today.filter(
            class_year_id=class_year_id
        )

    if subject_id and subject_id.isdigit():

        sessions_today = sessions_today.filter(
            subject_id=subject_id
        )

    total_students = students.count()

    present_today = AttendanceRecord.objects.filter(
        session__in=sessions_today
    ).count()

    attendance_rate = (
        round(
            (present_today / total_students) * 100,
            2
        )
        if total_students
        else 0
    )

    return JsonResponse(
        {
            "total_students": total_students,
            "present_today": present_today,
            "attendance_rate": attendance_rate,
        }
    )


# ============================================================
# GET SUBJECTS BY CLASS YEAR
# ============================================================

def get_subjects_by_class_year(request):

    class_year_id = request.GET.get(
        "class_year_id"
    )

    subjects = Subject.objects.filter(
        year_id=class_year_id
    )

    data = [
        {
            "id": subject.id,
            "name": subject.name
        }
        for subject in subjects
    ]

    return JsonResponse(
        data,
        safe=False
    )


# ============================================================
# GENERATE QR
# ============================================================

@login_required
def generate_qr(request):

    # --------------------------------------------------------
    # If user directly opens:
    # /generate-qr/
    #
    # Redirect to dashboard.
    # --------------------------------------------------------

    if request.method == "GET":

        return redirect("dashboard")

    # --------------------------------------------------------
    # Get form values
    # --------------------------------------------------------

    class_year_id = request.POST.get(
        "ClassYears"
    )

    subject_id = request.POST.get(
        "Subject"
    )

    # --------------------------------------------------------
    # Get location
    # --------------------------------------------------------

    try:

        latitude = float(
            request.POST.get("latitude")
            or 18.5204
        )

        longitude = float(
            request.POST.get("longitude")
            or 73.8567
        )

    except (
        TypeError,
        ValueError
    ):

        latitude = 18.5204

        longitude = 73.8567

    # --------------------------------------------------------
    # Get Subject and Class Year
    # --------------------------------------------------------

    try:

        subject = Subject.objects.get(
            id=subject_id
        )

        class_year = ClassYear.objects.get(
            id=class_year_id
        )

    except (
        Subject.DoesNotExist,
        ClassYear.DoesNotExist,
        ValueError,
        TypeError
    ):

        messages.error(
            request,
            "Please select a valid Class Year and Subject."
        )

        return redirect("dashboard")

    # --------------------------------------------------------
    # QR expiry
    # --------------------------------------------------------

    expiry = (
        timezone.now()
        + timedelta(
            minutes=QR_EXPIRY_MINUTES
        )
    )

    # --------------------------------------------------------
    # Create Attendance Session
    # --------------------------------------------------------

    session = AttendanceSession.objects.create(

        teacher=request.user,

        subject=subject,

        class_year=class_year,

        date=timezone.localdate(),

        expires_at=expiry,

        token=uuid.uuid4(),

        latitude=latitude,

        longitude=longitude,
    )

    # --------------------------------------------------------
    # Build Student Scan URL
    # --------------------------------------------------------

    scan_url = build_scan_url(
        request,
        session.token
    )

    # --------------------------------------------------------
    # Generate QR image
    # --------------------------------------------------------

    qr = qrcode.make(scan_url)

    buffer = io.BytesIO()

    qr.save(
        buffer,
        format="PNG"
    )

    qr_image = base64.b64encode(
        buffer.getvalue()
    ).decode()

    # --------------------------------------------------------
    # Display QR
    # --------------------------------------------------------

    return render(
        request,
        "core/qr_display.html",
        {
            "qr_image": qr_image,
            "expires_at": expiry.isoformat(),
            "scan_url": scan_url,
        }
    )


# ============================================================
# EXPORT ATTENDANCE
# ============================================================

@login_required
def export_attendance(request):

    wb = Workbook()

    ws = wb.active

    ws.title = "Attendance Records"

    ws.append(
        [
            "Class",
            "Roll No.",
            "Name",
            "Subject",
            "Date",
            "Time",
        ]
    )

    today = timezone.localdate()

    sessions_today = AttendanceSession.objects.filter(
        teacher=request.user,
        date=today
    )

    records = (
        AttendanceRecord.objects
        .select_related(
            "student",
            "session__subject",
            "student__class_year",
            "session",
        )
        .filter(
            session__in=sessions_today
        )
    )

    for record in records:

        ws.append(
            [
                record.student.class_year.name,
                record.student.roll_number,
                record.student.name,
                record.session.subject.name,
                record.session.date.strftime(
                    "%Y-%m-%d"
                ),
                timezone.localtime(
                    record.timestamp
                ).strftime("%H:%M:%S"),
            ]
        )

    response = HttpResponse(
        content_type=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        )
    )

    response[
        "Content-Disposition"
    ] = (
        "attachment; "
        "filename=today_attendance.xlsx"
    )

    wb.save(response)

    return response


# ============================================================
# ATTENDANCE EXPIRED
# ============================================================

def attendance_expired(request):

    return render(
        request,
        "core/attendance_expired.html"
    )


# ============================================================
# ATTENDANCE SUCCESS
# ============================================================

def attendance_success(request):

    return render(
        request,
        "core/attendance_success.html"
    )


# ============================================================
# MARK ATTENDANCE
# ============================================================

def mark_attendance(request, token):

    session = get_object_or_404(
        AttendanceSession,
        token=token
    )

    # --------------------------------------------------------
    # Check QR expiry
    # --------------------------------------------------------

    if is_session_expired(
        session.expires_at
    ):

        return render(
            request,
            "core/attendance_expired.html"
        )

    # --------------------------------------------------------
    # Student submits attendance
    # --------------------------------------------------------

    if request.method == "POST":

        name = request.POST.get(
            "name",
            ""
        ).strip()

        roll_number = request.POST.get(
            "roll_number",
            ""
        ).strip()

        # ----------------------------------------------------
        # Validate input
        # ----------------------------------------------------

        if not name or not roll_number:

            messages.error(
                request,
                "Please fill out all fields."
            )

            return redirect(
                "mark_attendance",
                token=session.token
            )

        # ----------------------------------------------------
        # Find student
        # ----------------------------------------------------

        student = (
            Student.objects
            .filter(
                roll_number=roll_number,
                class_year=session.class_year
            )
            .first()
        )

        if student is None:

            messages.error(
                request,
                "Student not found for this class. "
                "Check your roll number."
            )

            return redirect(
                "mark_attendance",
                token=session.token
            )

        # ----------------------------------------------------
        # Prevent duplicate attendance
        # ----------------------------------------------------

        if AttendanceRecord.objects.filter(
            session=session,
            student=student
        ).exists():

            messages.warning(
                request,
                "Attendance already marked."
            )

            return redirect(
                "mark_attendance",
                token=session.token
            )

        # ----------------------------------------------------
        # Create attendance record
        # ----------------------------------------------------

        try:

            AttendanceRecord.objects.create(
                session=session,
                student=student,
                name=student.name,
                roll_number=student.roll_number,
            )

        except IntegrityError:

            messages.warning(
                request,
                "Attendance has already been marked "
                "for this session."
            )

            return redirect(
                "mark_attendance",
                token=session.token
            )

        # ----------------------------------------------------
        # Success
        # ----------------------------------------------------

        return render(
            request,
            "core/attendance_success.html",
            {
                "session": session,
                "student": student,
            }
        )

    # --------------------------------------------------------
    # Show student attendance form
    # --------------------------------------------------------

    return render(
        request,
        "core/student_mark_attendance.html",
        {
            "session": session
        }
    )