from django.contrib import admin
from .models import Quiz, Question, Option, QuizSubmission, Answer

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'start_date', 'end_date', 'is_published', 'total_questions']
    list_filter = ['is_published', 'start_date', 'course']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'question_type', 'marks', 'order']
    list_filter = ['question_type', 'quiz']
    search_fields = ['question_text']
    ordering = ['quiz', 'order']

@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ['question', 'option_text', 'is_correct', 'order']
    list_filter = ['is_correct']
    search_fields = ['option_text']

@admin.register(QuizSubmission)
class QuizSubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'quiz', 'start_time', 'is_submitted', 'marks_obtained']
    list_filter = ['is_submitted', 'start_time']
    search_fields = ['student__username', 'quiz__title']
    readonly_fields = ['start_time']

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['submission', 'question', 'is_correct', 'marks_obtained']
    list_filter = ['is_correct']
    search_fields = ['submission__student__username', 'question__question_text']
