from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Assignment, AssignmentSubmission
from .serializers import (
    AssignmentSerializer, AssignmentDetailSerializer,
    AssignmentSubmissionSerializer, AssignmentSubmissionListSerializer
)
from courses.models import Course

class AssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['course']
    search_fields = ['title', 'description']
    ordering_fields = ['due_date', 'created_at']
    ordering = ['-due_date']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Assignment.objects.all()
        elif user.is_teacher:
            return Assignment.objects.filter(course__instructor=user)
        else:
            return Assignment.objects.filter(
                course__enrollments__student=user,
                course__enrollments__status='active'
            ).distinct()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AssignmentDetailSerializer
        return AssignmentSerializer
    
    def perform_create(self, serializer):
        course_id = self.request.data.get('course')
        try:
            course = Course.objects.get(id=course_id)
            if self.request.user != course.instructor and not self.request.user.is_staff:
                raise PermissionError('Only course instructor can create assignments')
            serializer.save()
        except Course.DoesNotExist:
            raise ValueError('Course not found')

class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['assignment', 'student', 'status']
    ordering_fields = ['submission_date', 'marks_obtained']
    ordering = ['-submission_date']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return AssignmentSubmission.objects.all()
        elif user.is_teacher:
            return AssignmentSubmission.objects.filter(
                assignment__course__instructor=user
            )
        else:
            return AssignmentSubmission.objects.filter(student=user)
    
    def perform_create(self, serializer):
        serializer.save(student=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def grade(self, request, pk=None):
        submission = self.get_object()
        assignment = submission.assignment
        
        if request.user != assignment.course.instructor and not request.user.is_staff:
            return Response(
                {'error': 'Only course instructor can grade submissions.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        marks = request.data.get('marks_obtained')
        feedback = request.data.get('feedback', '')
        
        if marks is None or marks < 0 or marks > assignment.total_marks:
            return Response(
                {'error': f'Marks must be between 0 and {assignment.total_marks}.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        submission.marks_obtained = marks
        submission.feedback = feedback
        submission.status = 'graded'
        submission.graded_by = request.user
        submission.save()
        
        serializer = AssignmentSubmissionSerializer(submission)
        return Response(serializer.data)
