from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import CustomUser

class Course(models.Model):
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('published', _('Published')),
        ('archived', _('Archived')),
    )
    
    title = models.CharField(
        max_length=255,
        help_text=_('Course title')
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text=_('Course code/identifier')
    )
    description = models.TextField(
        help_text=_('Course description')
    )
    instructor = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='courses_taught',
        limit_choices_to={'role': 'teacher'},
        help_text=_('Course instructor')
    )
    thumbnail = models.ImageField(
        upload_to='course_thumbnails/',
        null=True,
        blank=True,
        help_text=_('Course thumbnail image')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text=_('Course status')
    )
    credits = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        default=3,
        help_text=_('Course credits')
    )
    max_students = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text=_('Maximum number of students')
    )
    capacity = models.IntegerField(
        default=0,
        help_text=_('Current student count')
    )
    start_date = models.DateField(
        help_text=_('Course start date')
    )
    end_date = models.DateField(
        help_text=_('Course end date')
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether course is active')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Course')
        verbose_name_plural = _('Courses')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['status']),
            models.Index(fields=['instructor']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.title}"
    
    @property
    def is_full(self):
        return self.capacity >= self.max_students

class Enrollment(models.Model):
    STATUS_CHOICES = (
        ('active', _('Active')),
        ('completed', _('Completed')),
        ('dropped', _('Dropped')),
    )
    
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'role': 'student'},
        help_text=_('Enrolled student')
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
        help_text=_('Enrolled course')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        help_text=_('Enrollment status')
    )
    enrolled_date = models.DateTimeField(auto_now_add=True)
    completion_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('Date when course was completed')
    )
    
    class Meta:
        verbose_name = _('Enrollment')
        verbose_name_plural = _('Enrollments')
        unique_together = ['student', 'course']
        ordering = ['-enrolled_date']
        indexes = [
            models.Index(fields=['student', 'course']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.student.username} - {self.course.code}"
