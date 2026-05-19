from django.contrib import admin
from .models import Assignment, AssignmentSubmission

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'due_date', 'total_marks', 'passing_marks']
    list_filter = ['course', 'due_date']
    search_fields = ['title', 'description', 'course__code']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'student', 'submission_date', 'status', 'marks_obtained']
    list_filter = ['status', 'submission_date']
    search_fields = ['student__username', 'assignment__title']
    readonly_fields = ['submission_date', 'graded_date']
