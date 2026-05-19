from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from courses.models import Course
from users.models import CustomUser

class Quiz(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='quizzes',
        help_text=_('Course associated with quiz')
    )
    title = models.CharField(
        max_length=255,
        help_text=_('Quiz title')
    )
    description = models.TextField(
        blank=True,
        help_text=_('Quiz description')
    )
    total_questions = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text=_('Total number of questions')
    )
    total_marks = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(1000)],
        default=100,
        help_text=_('Total marks for quiz')
    )
    passing_marks = models.IntegerField(
        validators=[MinValueValidator(0)],
        default=40,
        help_text=_('Passing marks for quiz')
    )
    duration_minutes = models.IntegerField(
        validators=[MinValueValidator(1)],
        default=30,
        help_text=_('Quiz duration in minutes')
    )
    start_date = models.DateTimeField(
        help_text=_('Quiz start date and time')
    )
    end_date = models.DateTimeField(
        help_text=_('Quiz end date and time')
    )
    is_published = models.BooleanField(
        default=False,
        help_text=_('Whether quiz is published')
    )
    show_answers = models.BooleanField(
        default=False,
        help_text=_('Show correct answers to students after submission')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Quiz')
        verbose_name_plural = _('Quizzes')
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['course']),
            models.Index(fields=['is_published']),
        ]
    
    def __str__(self):
        return f"{self.course.code} - {self.title}"

class Question(models.Model):
    QUESTION_TYPE_CHOICES = (
        ('mcq', _('Multiple Choice')),
        ('short_answer', _('Short Answer')),
        ('long_answer', _('Long Answer')),
        ('true_false', _('True/False')),
    )
    
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions',
        help_text=_('Quiz this question belongs to')
    )
    question_text = models.TextField(
        help_text=_('Question text')
    )
    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPE_CHOICES,
        help_text=_('Type of question')
    )
    marks = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=1,
        help_text=_('Marks for this question')
    )
    order = models.IntegerField(
        default=0,
        help_text=_('Display order')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')
        ordering = ['quiz', 'order']
        indexes = [
            models.Index(fields=['quiz']),
        ]
    
    def __str__(self):
        return f"{self.quiz.title} - Q{self.order}"

class Option(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='options',
        help_text=_('Question this option belongs to')
    )
    option_text = models.TextField(
        help_text=_('Option text')
    )
    is_correct = models.BooleanField(
        default=False,
        help_text=_('Is this the correct option')
    )
    order = models.IntegerField(
        default=0,
        help_text=_('Display order')
    )
    
    class Meta:
        verbose_name = _('Option')
        verbose_name_plural = _('Options')
        ordering = ['question', 'order']
    
    def __str__(self):
        return f"{self.question.quiz.title} - Option {self.order}"

class QuizSubmission(models.Model):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='submissions',
        help_text=_('Quiz submitted')
    )
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='quiz_submissions',
        limit_choices_to={'role': 'student'},
        help_text=_('Student who submitted')
    )
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('Time when student submitted quiz')
    )
    marks_obtained = models.IntegerField(
        validators=[MinValueValidator(0)],
        null=True,
        blank=True,
        help_text=_('Marks obtained')
    )
    is_submitted = models.BooleanField(
        default=False,
        help_text=_('Whether quiz is submitted')
    )
    
    class Meta:
        verbose_name = _('Quiz Submission')
        verbose_name_plural = _('Quiz Submissions')
        unique_together = ['quiz', 'student']
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['quiz', 'student']),
        ]
    
    def __str__(self):
        return f"{self.student.username} - {self.quiz.title}"

class Answer(models.Model):
    submission = models.ForeignKey(
        QuizSubmission,
        on_delete=models.CASCADE,
        related_name='answers',
        help_text=_('Quiz submission')
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        help_text=_('Question answered')
    )
    selected_option = models.ForeignKey(
        Option,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text=_('Selected option for MCQ')
    )
    answer_text = models.TextField(
        blank=True,
        help_text=_('Answer text for short/long answer questions')
    )
    is_correct = models.BooleanField(
        null=True,
        help_text=_('Whether answer is correct')
    )
    marks_obtained = models.IntegerField(
        validators=[MinValueValidator(0)],
        null=True,
        blank=True,
        help_text=_('Marks obtained for this answer')
    )
    
    class Meta:
        verbose_name = _('Answer')
        verbose_name_plural = _('Answers')
        unique_together = ['submission', 'question']
    
    def __str__(self):
        return f"{self.submission.student.username} - Q{self.question.order}"
