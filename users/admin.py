from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, ParentStudent

@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'profile_picture', 'bio', 'phone_number', 'department', 'registration_number')}),
    )
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'created_at', 'department']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-created_at']

@admin.register(ParentStudent)
class ParentStudentAdmin(admin.ModelAdmin):
    list_display = ['parent', 'student', 'relationship', 'is_primary', 'created_at']
    list_filter = ['relationship', 'is_primary', 'created_at']
    search_fields = ['parent__username', 'student__username', 'parent__email', 'student__email']
    ordering = ['-is_primary', '-created_at']

