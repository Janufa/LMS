from rest_framework import serializers
from .models import StudyMaterial
from users.serializers import UserListSerializer

class StudyMaterialSerializer(serializers.ModelSerializer):
    uploaded_by = UserListSerializer(read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    
    class Meta:
        model = StudyMaterial
        fields = [
            'id', 'course', 'course_code', 'title', 'description', 'material_type',
            'file', 'external_link', 'uploaded_by', 'order', 'is_published',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uploaded_by', 'created_at', 'updated_at']

class StudyMaterialListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyMaterial
        fields = ['id', 'course', 'title', 'material_type', 'is_published', 'created_at']
