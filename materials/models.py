from django.db import models
from django.utils.translation import gettext_lazy as _
from courses.models import Course
from users.models import CustomUser

class StudyMaterial(models.Model):
    MATERIAL_TYPE_CHOICES = (
        ('pdf', _('PDF')),
        ('video', _('Video')),
        ('document', _('Document')),
        ('image', _('Image')),
        ('link', _('Link')),
        ('other', _('Other')),
    )
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='materials',
        help_text=_('Course associated with material')
    )
    title = models.CharField(
        max_length=255,
        help_text=_('Material title')
    )
    description = models.TextField(
        blank=True,
        help_text=_('Material description')
    )
    material_type = models.CharField(
        max_length=20,
        choices=MATERIAL_TYPE_CHOICES,
        help_text=_('Type of material')
    )
    file = models.FileField(
        upload_to='course_materials/',
        null=True,
        blank=True,
        help_text=_('Material file')
    )
    external_link = models.URLField(
        blank=True,
        help_text=_('External link to material')
    )
    uploaded_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_materials',
        help_text=_('User who uploaded material')
    )
    order = models.IntegerField(
        default=0,
        help_text=_('Display order')
    )
    is_published = models.BooleanField(
        default=True,
        help_text=_('Whether material is visible to students')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Study Material')
        verbose_name_plural = _('Study Materials')
        ordering = ['course', 'order', '-created_at']
        indexes = [
            models.Index(fields=['course']),
            models.Index(fields=['is_published']),
        ]
    
    def __str__(self):
        return f"{self.course.code} - {self.title}"
