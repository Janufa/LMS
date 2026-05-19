from django.contrib import admin
from .models import StudyMaterial

@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'material_type', 'is_published', 'created_at']
    list_filter = ['material_type', 'is_published', 'created_at']
    search_fields = ['title', 'description', 'course__code']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['course', 'order']
