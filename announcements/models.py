from django.db import models
from django.utils.translation import gettext_lazy as _
from courses.models import Course
from users.models import CustomUser

class Announcement(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='announcements',
        help_text=_('Course for which announcement is posted')
    )
    title = models.CharField(
        max_length=255,
        help_text=_('Announcement title')
    )
    content = models.TextField(
        help_text=_('Announcement content')
    )
    posted_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='announcements_posted',
        help_text=_('User who posted announcement')
    )
    attachment = models.FileField(
        upload_to='announcements/',
        null=True,
        blank=True,
        help_text=_('Announcement attachment')
    )
    is_important = models.BooleanField(
        default=False,
        help_text=_('Mark as important announcement')
    )
    is_published = models.BooleanField(
        default=True,
        help_text=_('Whether announcement is visible to students')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Announcement')
        verbose_name_plural = _('Announcements')
        ordering = ['-is_important', '-created_at']
        indexes = [
            models.Index(fields=['course']),
            models.Index(fields=['is_published']),
        ]
    
    def __str__(self):
        return f"{self.course.code} - {self.title}"

class AnnouncementRead(models.Model):
    """Track which students have read each announcement"""
    announcement = models.ForeignKey(
        Announcement,
        on_delete=models.CASCADE,
        related_name='read_by',
        help_text=_('Announcement read')
    )
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='announcements_read',
        limit_choices_to={'role': 'student'},
        help_text=_('Student who read')
    )
    read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Announcement Read')
        verbose_name_plural = _('Announcements Read')
        unique_together = ['announcement', 'student']
        indexes = [
            models.Index(fields=['announcement']),
            models.Index(fields=['student']),
        ]
    
    def __str__(self):
        return f"{self.student.username} - {self.announcement.title}"
