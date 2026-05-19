from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Course, Enrollment
from .serializers import CourseSerializer, CourseDetailSerializer, EnrollmentSerializer, EnrollmentListSerializer
from users.models import CustomUser

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'is_active', 'instructor']
    search_fields = ['title', 'code', 'description']
    ordering_fields = ['created_at', 'title', 'start_date']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseSerializer
    
    def perform_create(self, serializer):
        if self.request.user.is_teacher or self.request.user.is_staff:
            serializer.save(instructor=self.request.user)
        else:
            return Response(
                {'error': 'Only teachers can create courses.'},
                status=status.HTTP_403_FORBIDDEN
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def enroll(self, request, pk=None):
        course = self.get_object()
        student = request.user
        
        if student.role != 'student':
            return Response(
                {'error': 'Only students can enroll in courses.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if course.is_full:
            return Response(
                {'error': 'Course is full.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        enrollment, created = Enrollment.objects.get_or_create(
            student=student,
            course=course,
            defaults={'status': 'active'}
        )
        
        if created:
            course.capacity += 1
            course.save()
            return Response(
                {'message': 'Successfully enrolled in course.'},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error': 'Already enrolled in this course.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unenroll(self, request, pk=None):
        course = self.get_object()
        student = request.user
        
        try:
            enrollment = Enrollment.objects.get(student=student, course=course)
            enrollment.status = 'dropped'
            enrollment.save()
            course.capacity = max(0, course.capacity - 1)
            course.save()
            return Response({'message': 'Successfully unenrolled from course.'})
        except Enrollment.DoesNotExist:
            return Response(
                {'error': 'Not enrolled in this course.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def students(self, request, pk=None):
        course = self.get_object()
        enrollments = course.enrollments.filter(status='active')
        serializer = EnrollmentListSerializer(enrollments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_courses(self, request):
        user = request.user
        if user.is_teacher or user.is_staff:
            courses = Course.objects.filter(instructor=user)
        else:
            courses = Course.objects.filter(
                enrollments__student=user,
                enrollments__status='active'
            ).distinct()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'student', 'course']
    ordering_fields = ['enrolled_date']
    ordering = ['-enrolled_date']
    
    def perform_create(self, serializer):
        student = CustomUser.objects.get(pk=self.request.data.get('student'))
        if self.request.user != student and not self.request.user.is_staff:
            return Response(
                {'error': 'You can only enroll yourself.'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()
