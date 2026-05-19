from rest_framework import serializers
from .models import Course, Enrollment
from users.serializers import UserListSerializer

class CourseSerializer(serializers.ModelSerializer):
    instructor = UserListSerializer(read_only=True)
    instructor_id = serializers.IntegerField(write_only=True, source='instructor', required=False)
    student_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'code', 'description', 'instructor', 'instructor_id',
            'thumbnail', 'status', 'credits', 'max_students', 'capacity',
            'start_date', 'end_date', 'is_active', 'student_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'capacity', 'created_at', 'updated_at']
    
    def get_student_count(self, obj):
        return obj.enrollments.filter(status='active').count()

class EnrollmentSerializer(serializers.ModelSerializer):
    student = UserListSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    
    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'status', 'enrolled_date', 'completion_date']
        read_only_fields = ['id', 'enrolled_date', 'completion_date']

class CourseDetailSerializer(CourseSerializer):
    enrollments = EnrollmentSerializer(many=True, read_only=True)
    
    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + ['enrollments']

class EnrollmentListSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    
    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'student_name', 'course', 'course_code', 'status', 'enrolled_date']
