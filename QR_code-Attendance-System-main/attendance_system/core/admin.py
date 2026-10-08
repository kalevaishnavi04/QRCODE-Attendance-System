from django.contrib import admin

from .models import (AttendanceRecord, AttendanceSession, ClassYear, Student,
                     Subject)


@admin.register(ClassYear)
class ClassYearAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'year')
    list_filter = ('year',)
    filter_horizontal = ('teachers',)  # Teachers: select karun ">" dabva


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'roll_number', 'class_year')
    list_filter = ('class_year',)
    search_fields = ('name', 'roll_number')


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ('subject', 'class_year', 'teacher', 'date', 'expires_at')


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('name', 'roll_number', 'session', 'timestamp')
