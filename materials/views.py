from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import StudyMaterial
from .serializers import StudyMaterialSerializer, StudyMaterialListSerializer
from courses.models import Course

class StudyMaterialViewSet(viewsets.ModelViewSet):
    serializer_class = StudyMaterialSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['course', 'material_type', 'is_published']
    search_fields = ['title', 'description']
    ordering_fields = ['order', 'created_at']
    ordering = ['order', '-created_at']
    
    def get_queryset(self):
        user = self.user
        if user.is_staff:
            return StudyMaterial.objects.all()
        elif user.is_teacher:
            return StudyMaterial.objects.filter(course__instructor=user)
        else:
            return StudyMaterial.objects.filter(
                course__enrollments__student=user,
                course__enrollments__status='active',
                is_published=True
            ).distinct()
    
    @property
    def user(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.action == 'list':
            return StudyMaterialListSerializer
        return StudyMaterialSerializer
    
    def perform_create(self, serializer):
        course_id = self.request.data.get('course')
        try:
            course = Course.objects.get(id=course_id)
            if self.request.user != course.instructor and not self.request.user.is_staff:
                return status.HTTP_403_FORBIDDEN
            serializer.save(uploaded_by=self.request.user)
        except Course.DoesNotExist:
            return status.HTTP_404_NOT_FOUND
