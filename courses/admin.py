from django.contrib import admin
from .models import Course, Enrollment

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'instructor', 'status', 'start_date', 'end_date', 'is_active']
    list_filter = ['status', 'is_active', 'start_date']
    search_fields = ['code', 'title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'status', 'enrolled_date']
    list_filter = ['status', 'enrolled_date']
    search_fields = ['student__username', 'course__code']
    readonly_fields = ['enrolled_date']
