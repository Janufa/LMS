from rest_framework import serializers
from .models import Announcement, AnnouncementRead
from users.serializers import UserListSerializer

class AnnouncementSerializer(serializers.ModelSerializer):
    posted_by = UserListSerializer(read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    
    class Meta:
        model = Announcement
        fields = [
            'id', 'course', 'course_code', 'title', 'content', 'posted_by',
            'attachment', 'is_important', 'is_published', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'posted_by', 'created_at', 'updated_at']

class AnnouncementDetailSerializer(AnnouncementSerializer):
    read_count = serializers.SerializerMethodField()
    
    class Meta(AnnouncementSerializer.Meta):
        fields = AnnouncementSerializer.Meta.fields + ['read_count']
    
    def get_read_count(self, obj):
        return obj.read_by.count()

class AnnouncementListSerializer(serializers.ModelSerializer):
    posted_by_name = serializers.CharField(source='posted_by.get_full_name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    
    class Meta:
        model = Announcement
        fields = ['id', 'course_code', 'title', 'posted_by_name', 'is_important', 'created_at']
