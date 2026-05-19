from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import time
from .models import Attendance
from .serializers import (
    AttendanceSerializer, AttendanceMarkSerializer,
    AttendanceApprovalSerializer, AttendanceListSerializer
)
from courses.models import Enrollment

class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'course', 'date', 'status']
    ordering_fields = ['date', 'student']
    ordering = ['-date']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Attendance.objects.all()
        elif user.is_teacher:
            return Attendance.objects.filter(course__instructor=user)
        elif user.role == 'parent':
            # Parents can see their children's attendance
            from users.models import ParentStudent
            student_ids = ParentStudent.objects.filter(
                parent=user
            ).values_list('student_id', flat=True)
            return Attendance.objects.filter(student_id__in=student_ids)
        else:
            return Attendance.objects.filter(student=user)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def mark_present(self, request):
        """Mark student as present with optional late arrival details"""
        student = request.user
        course_id = request.data.get('course')
        status_mark = request.data.get('status', 'present')  # 'present' or 'late'
        late_message = request.data.get('late_message', '')
        late_photo = request.files.get('late_photo')
        
        if not course_id:
            return Response(
                {'error': 'Course ID is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify student is enrolled in course
        try:
            enrollment = Enrollment.objects.get(
                student=student,
                course_id=course_id,
                status='active'
            )
        except Enrollment.DoesNotExist:
            return Response(
                {'error': 'Student is not enrolled in this course.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get current time
        current_time = timezone.now().time()
        cutoff_time = time(8, 30)
        
        # Determine status
        if current_time > cutoff_time and status_mark == 'present':
            status_mark = 'late'
        
        # Validate late arrival requirements
        if status_mark == 'late':
            if not late_message:
                return Response(
                    {'error': 'Message is required for late arrivals.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if not late_photo:
                return Response(
                    {'error': 'Photo proof is required for late arrivals.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Create or update attendance
        today = timezone.now().date()
        attendance, created = Attendance.objects.get_or_create(
            student=student,
            course_id=course_id,
            date=today,
            defaults={
                'status': status_mark,
                'time_marked': current_time,
                'late_message': late_message,
                'late_photo': late_photo
            }
        )
        
        if not created:
            attendance.status = status_mark
            attendance.time_marked = current_time
            attendance.late_message = late_message
            if late_photo:
                attendance.late_photo = late_photo
            attendance.save()
        
        serializer = AttendanceSerializer(attendance)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def approve_late(self, request, pk=None):
        """Teacher approves late arrival"""
        attendance = self.get_object()
        
        if request.user != attendance.course.instructor and not request.user.is_staff:
            return Response(
                {'error': 'Only course instructor can approve late arrivals.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if attendance.status != 'late':
            return Response(
                {'error': 'Only late arrivals can be approved.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        attendance.status = 'excused'
        attendance.approved_by = request.user
        attendance.approval_remarks = request.data.get('approval_remarks', '')
        attendance.save()
        
        serializer = AttendanceSerializer(attendance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def reject_late(self, request, pk=None):
        """Teacher rejects late arrival and marks as absent"""
        attendance = self.get_object()
        
        if request.user != attendance.course.instructor and not request.user.is_staff:
            return Response(
                {'error': 'Only course instructor can reject late arrivals.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if attendance.status != 'late':
            return Response(
                {'error': 'Only late arrivals can be rejected.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        attendance.status = 'absent'
        attendance.approved_by = request.user
        attendance.approval_remarks = request.data.get('approval_remarks', '')
        attendance.save()
        
        serializer = AttendanceSerializer(attendance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def course_attendance_report(self, request):
        """Get attendance report for a course"""
        course_id = request.query_params.get('course')
        date = request.query_params.get('date')
        
        if not course_id:
            return Response(
                {'error': 'Course ID is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = Attendance.objects.filter(course_id=course_id)
        
        if date:
            queryset = queryset.filter(date=date)
        
        # Check permission
        user = request.user
        if not user.is_staff:
            try:
                course = queryset.first().course if queryset.exists() else None
                if not course or user != course.instructor:
                    return Response(
                        {'error': 'You do not have permission to view this report.'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except:
                return Response(
                    {'error': 'Course not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        serializer = AttendanceListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def student_attendance_history(self, request):
        """Get attendance history for a student"""
        course_id = request.query_params.get('course')
        
        if not course_id:
            return Response(
                {'error': 'Course ID is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = Attendance.objects.filter(
            student=request.user,
            course_id=course_id
        )
        
        # Get statistics
        total = queryset.count()
        present = queryset.filter(status='present').count()
        absent = queryset.filter(status='absent').count()
        late = queryset.filter(status='late').count()
        excused = queryset.filter(status='excused').count()
        
        attendance_percentage = (present / total * 100) if total > 0 else 0
        
        serializer = AttendanceListSerializer(queryset, many=True)
        
        return Response({
            'records': serializer.data,
            'statistics': {
                'total': total,
                'present': present,
                'absent': absent,
                'late': late,
                'excused': excused,
                'attendance_percentage': round(attendance_percentage, 2)
            }
        })
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def children_attendance(self, request):
        """Parents can view their children's attendance"""
        user = request.user
        
        if user.role != 'parent':
            return Response(
                {'error': 'Only parents can access this endpoint.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from users.models import ParentStudent
        course_id = request.query_params.get('course')
        date = request.query_params.get('date')
        student_id = request.query_params.get('student')
        
        # Get all children of the parent
        children = ParentStudent.objects.filter(parent=user).values_list('student_id', flat=True)
        
        if not children:
            return Response(
                {'error': 'No children linked to this parent account.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Filter by specific student if provided
        if student_id:
            if int(student_id) not in children:
                return Response(
                    {'error': 'This student is not your child.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            children = [int(student_id)]
        
        queryset = Attendance.objects.filter(student_id__in=children)
        
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        if date:
            queryset = queryset.filter(date=date)
        
        serializer = AttendanceListSerializer(queryset, many=True)
        return Response({
            'children_attendance': serializer.data,
            'child_count': len(children)
        })
