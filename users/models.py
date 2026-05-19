from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import URLValidator
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', _('Admin')),
        ('teacher', _('Teacher')),
        ('student', _('Student')),
        ('parent', _('Parent')),
    )
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='student',
        help_text=_('User role in the system')
    )
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True,
        help_text=_('User profile picture')
    )
    bio = models.TextField(
        blank=True,
        help_text=_('User biography')
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        help_text=_('User phone number')
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('User department/faculty')
    )
    registration_number = models.CharField(
        max_length=50,
        blank=True,
        unique=True,
        help_text=_('Student registration number')
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether user account is active')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    @property
    def is_teacher(self):
        return self.role == 'teacher'
    
    @property
    def is_student(self):
        return self.role == 'student'
    
    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_staff


class ParentStudent(models.Model):
    """Model to link parents with their children (students)"""
    parent = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='children',
        limit_choices_to={'role': 'parent'},
        help_text=_('Parent user')
    )
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='parents',
        limit_choices_to={'role': 'student'},
        help_text=_('Student user')
    )
    relationship = models.CharField(
        max_length=50,
        default='parent',
        choices=[
            ('parent', _('Parent')),
            ('guardian', _('Guardian')),
            ('relative', _('Relative')),
        ],
        help_text=_('Relationship to student')
    )
    is_primary = models.BooleanField(
        default=False,
        help_text=_('Is this the primary parent/guardian')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Parent-Student Relationship')
        verbose_name_plural = _('Parent-Student Relationships')
        unique_together = ['parent', 'student']
        ordering = ['-is_primary', '-created_at']
    
    def __str__(self):
        return f"{self.parent.get_full_name()} - {self.student.get_full_name()}"
