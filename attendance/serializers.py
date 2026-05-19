from rest_framework import serializers
from .models import Attendance
from users.serializers import UserListSerializer

class AttendanceSerializer(serializers.ModelSerializer):
    student = UserListSerializer(read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    approved_by = UserListSerializer(read_only=True)
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'student', 'course', 'course_code', 'date', 'status', 'time_marked',
            'late_message', 'late_photo', 'marked_automatically', 'approved_by',
            'approval_remarks', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'marked_automatically']

class AttendanceMarkSerializer(serializers.ModelSerializer):
    """Serializer for marking attendance"""
    class Meta:
        model = Attendance
        fields = ['id', 'student', 'course', 'date', 'status', 'time_marked', 'late_message', 'late_photo']
        read_only_fields = ['id']
    
    def validate(self, data):
        status = data.get('status')
        late_message = data.get('late_message')
        late_photo = data.get('late_photo')
        
        if status == 'late':
            if not late_message:
                raise serializers.ValidationError(
                    {'late_message': 'Message is required for late arrivals.'}
                )
            if not late_photo:
                raise serializers.ValidationError(
                    {'late_photo': 'Photo is required for late arrivals.'}
                )
        
        return data

class AttendanceApprovalSerializer(serializers.ModelSerializer):
    """Serializer for approving late arrivals"""
    class Meta:
        model = Attendance
        fields = ['id', 'approval_remarks']

class AttendanceListSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    
    class Meta:
        model = Attendance
        fields = ['id', 'student', 'student_name', 'course_code', 'date', 'status', 'time_marked']
