from django.contrib import admin
from .models import Announcement, AnnouncementRead

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'posted_by', 'is_important', 'is_published', 'created_at']
    list_filter = ['is_important', 'is_published', 'created_at', 'course']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-is_important', '-created_at']

@admin.register(AnnouncementRead)
class AnnouncementReadAdmin(admin.ModelAdmin):
    list_display = ['announcement', 'student', 'read_at']
    list_filter = ['read_at']
    search_fields = ['announcement__title', 'student__username']
    readonly_fields = ['read_at']
