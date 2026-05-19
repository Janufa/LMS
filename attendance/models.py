from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from courses.models import Course
from users.models import CustomUser
from datetime import datetime, time

class Attendance(models.Model):
    STATUS_CHOICES = (
        ('present', _('Present')),
        ('absent', _('Absent')),
        ('late', _('Late')),
        ('excused', _('Excused')),
    )
    
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='attendance_records',
        limit_choices_to={'role': 'student'},
        help_text=_('Student in attendance')
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='attendance_records',
        help_text=_('Course for which attendance is marked')
    )
    date = models.DateField(
        default=timezone.now,
        help_text=_('Attendance date')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='absent',
        help_text=_('Attendance status')
    )
    time_marked = models.TimeField(
        null=True,
        blank=True,
        help_text=_('Time when student marked present/late')
    )
    late_message = models.TextField(
        blank=True,
        help_text=_('Student message explaining late arrival')
    )
    late_photo = models.ImageField(
        upload_to='late_arrivals/',
        null=True,
        blank=True,
        help_text=_('Photo proof for late arrival')
    )
    marked_automatically = models.BooleanField(
        default=False,
        help_text=_('Whether status was automatically marked as absent')
    )
    approved_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_attendance',
        help_text=_('Teacher who approved late arrival')
    )
    approval_remarks = models.TextField(
        blank=True,
        help_text=_('Teacher remarks on late arrival approval')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Attendance')
        verbose_name_plural = _('Attendance Records')
        unique_together = ['student', 'course', 'date']
        ordering = ['-date', 'student']
        indexes = [
            models.Index(fields=['student', 'date']),
            models.Index(fields=['course', 'date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.student.username} - {self.course.code} - {self.date}"
    
    @property
    def is_late(self):
        return self.status == 'late'
    
    @property
    def is_absent(self):
        return self.status == 'absent'
    
    @staticmethod
    def mark_absent_after_830():
        """
        Automatically mark students as absent if they haven't marked attendance by 8:30 AM.
        This should be run daily at 8:31 AM.
        """
        from django.db.models import Q
        
        current_time = time(8, 30)
        today = timezone.now().date()
        
        # Get all active courses
        active_courses = Course.objects.filter(is_active=True)
        
        for course in active_courses:
            # Get all enrolled students
            enrolled_students = course.enrollments.filter(status='active').values_list('student_id', flat=True)
            
            # Find students without any attendance record for today
            for student_id in enrolled_students:
                attendance, created = Attendance.objects.get_or_create(
                    student_id=student_id,
                    course=course,
                    date=today,
                    defaults={
                        'status': 'absent',
                        'marked_automatically': True
                    }
                )
