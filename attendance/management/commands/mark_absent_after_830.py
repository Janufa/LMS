from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from datetime import time
from attendance.models import Attendance
from courses.models import Course, Enrollment

class Command(BaseCommand):
    help = 'Automatically mark students as absent after 8:30 AM if they have not marked attendance'
    
    def handle(self, *args, **options):
        current_time = timezone.now().time()
        cutoff_time = time(8, 30)
        today = timezone.now().date()
        
        # Only run after 8:30 AM
        if current_time <= cutoff_time:
            self.stdout.write(
                self.style.WARNING(
                    f'Current time ({current_time}) is before 8:30 AM. Command should run after 8:30 AM.'
                )
            )
            return
        
        # Get all active courses
        active_courses = Course.objects.filter(is_active=True)
        total_marked = 0
        
        for course in active_courses:
            # Get all enrolled students
            enrolled_students = course.enrollments.filter(
                status='active'
            ).values_list('student_id', flat=True)
            
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
                
                if created:
                    total_marked += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully marked {total_marked} students as absent.'
            )
        )
