from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Announcement, AnnouncementRead
from .serializers import AnnouncementSerializer, AnnouncementDetailSerializer, AnnouncementListSerializer

class AnnouncementViewSet(viewsets.ModelViewSet):
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['course', 'is_important', 'is_published']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'is_important']
    ordering = ['-is_important', '-created_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Announcement.objects.all()
        elif user.is_teacher:
            return Announcement.objects.filter(course__instructor=user)
        else:
            return Announcement.objects.filter(
                course__enrollments__student=user,
                course__enrollments__status='active',
                is_published=True
            ).distinct()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AnnouncementDetailSerializer
        elif self.action == 'list':
            return AnnouncementListSerializer
        return AnnouncementSerializer
    
    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def mark_as_read(self, request, pk=None):
        """Mark announcement as read"""
        announcement = self.get_object()
        student = request.user
        
        if student.role != 'student':
            return Response(
                {'error': 'Only students can mark announcements as read.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        read_record, created = AnnouncementRead.objects.get_or_create(
            announcement=announcement,
            student=student
        )
        
        return Response({
            'message': 'Announcement marked as read.' if created else 'Already marked as read.'
        })
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def course_announcements(self, request):
        """Get all announcements for a course"""
        course_id = request.query_params.get('course')
        
        if not course_id:
            return Response(
                {'error': 'Course ID is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = request.user
        queryset = self.get_queryset().filter(course_id=course_id)
        
        serializer = AnnouncementListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def check_read_status(self, request, pk=None):
        """Check if current user has read this announcement"""
        announcement = self.get_object()
        is_read = AnnouncementRead.objects.filter(
            announcement=announcement,
            student=request.user
        ).exists()
        
        return Response({
            'announcement_id': announcement.id,
            'is_read': is_read
        })
