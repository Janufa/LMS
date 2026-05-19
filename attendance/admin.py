from django.contrib import admin
from .models import Attendance

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'date', 'status', 'time_marked', 'marked_automatically']
    list_filter = ['status', 'date', 'course', 'marked_automatically']
    search_fields = ['student__username', 'course__code']
    readonly_fields = ['marked_automatically', 'created_at', 'updated_at']
    ordering = ['-date', 'course']
    
    fieldsets = (
        ('Attendance Details', {
            'fields': ('student', 'course', 'date', 'status', 'time_marked')
        }),
        ('Late Arrival Information', {
            'fields': ('late_message', 'late_photo'),
            'classes': ('collapse',)
        }),
        ('Approval Information', {
            'fields': ('approved_by', 'approval_remarks'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('marked_automatically', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
