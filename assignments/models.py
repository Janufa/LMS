from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from courses.models import Course
from users.models import CustomUser

class Assignment(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='assignments',
        help_text=_('Course associated with assignment')
    )
    title = models.CharField(
        max_length=255,
        help_text=_('Assignment title')
    )
    description = models.TextField(
        help_text=_('Assignment description and instructions')
    )
    instructions = models.TextField(
        blank=True,
        help_text=_('Detailed instructions')
    )
    due_date = models.DateTimeField(
        help_text=_('Assignment due date')
    )
    total_marks = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(1000)],
        default=100,
        help_text=_('Total marks for assignment')
    )
    passing_marks = models.IntegerField(
        validators=[MinValueValidator(0)],
        default=40,
        help_text=_('Passing marks for assignment')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Assignment')
        verbose_name_plural = _('Assignments')
        ordering = ['-due_date']
        indexes = [
            models.Index(fields=['course']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return f"{self.course.code} - {self.title}"
    
    @property
    def is_overdue(self):
        return timezone.now() > self.due_date

class AssignmentSubmission(models.Model):
    STATUS_CHOICES = (
        ('submitted', _('Submitted')),
        ('graded', _('Graded')),
        ('late', _('Late Submission')),
    )
    
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions',
        help_text=_('Assignment submitted')
    )
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='assignment_submissions',
        limit_choices_to={'role': 'student'},
        help_text=_('Student who submitted')
    )
    submission_file = models.FileField(
        upload_to='assignments/',
        help_text=_('Submitted file')
    )
    submission_text = models.TextField(
        blank=True,
        help_text=_('Submission text content')
    )
    submission_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='submitted',
        help_text=_('Submission status')
    )
    marks_obtained = models.IntegerField(
        validators=[MinValueValidator(0)],
        null=True,
        blank=True,
        help_text=_('Marks obtained')
    )
    feedback = models.TextField(
        blank=True,
        help_text=_('Teacher feedback')
    )
    graded_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='graded_submissions',
        help_text=_('Teacher who graded')
    )
    graded_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('Date of grading')
    )
    
    class Meta:
        verbose_name = _('Assignment Submission')
        verbose_name_plural = _('Assignment Submissions')
        unique_together = ['assignment', 'student']
        ordering = ['-submission_date']
        indexes = [
            models.Index(fields=['assignment', 'student']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"
    
    @property
    def is_late(self):
        return self.submission_date > self.assignment.due_date
    
    @property
    def is_passing(self):
        if self.marks_obtained is None:
            return None
        return self.marks_obtained >= self.assignment.passing_marks
