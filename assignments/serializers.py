from rest_framework import serializers
from .models import Assignment, AssignmentSubmission
from users.serializers import UserListSerializer

class AssignmentSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(source='course.code', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    submission_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Assignment
        fields = [
            'id', 'course', 'course_code', 'title', 'description', 'instructions',
            'due_date', 'total_marks', 'passing_marks', 'is_overdue',
            'submission_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_submission_count(self, obj):
        return obj.submissions.count()

class AssignmentDetailSerializer(AssignmentSerializer):
    submissions = serializers.SerializerMethodField()
    
    class Meta(AssignmentSerializer.Meta):
        fields = AssignmentSerializer.Meta.fields + ['submissions']
    
    def get_submissions(self, obj):
        submissions = obj.submissions.all()
        serializer = AssignmentSubmissionListSerializer(submissions, many=True)
        return serializer.data

class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    student = UserListSerializer(read_only=True)
    graded_by = UserListSerializer(read_only=True)
    is_late = serializers.BooleanField(read_only=True)
    is_passing = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = AssignmentSubmission
        fields = [
            'id', 'assignment', 'student', 'submission_file', 'submission_text',
            'submission_date', 'status', 'marks_obtained', 'feedback', 'graded_by',
            'graded_date', 'is_late', 'is_passing'
        ]
        read_only_fields = ['id', 'submission_date', 'graded_date']

class AssignmentSubmissionListSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    
    class Meta:
        model = AssignmentSubmission
        fields = ['id', 'student', 'student_name', 'submission_date', 'status', 'marks_obtained']
