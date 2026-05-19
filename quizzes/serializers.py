from rest_framework import serializers
from .models import Quiz, Question, Option, QuizSubmission, Answer

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'option_text', 'is_correct', 'order']

class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'question_type', 'marks', 'order', 'options']

class QuizSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(source='course.code', read_only=True)
    question_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'course', 'course_code', 'title', 'description', 'total_questions',
            'total_marks', 'passing_marks', 'duration_minutes', 'start_date', 'end_date',
            'is_published', 'show_answers', 'question_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_question_count(self, obj):
        return obj.questions.count()

class QuizDetailSerializer(QuizSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta(QuizSerializer.Meta):
        fields = QuizSerializer.Meta.fields + ['questions']

class AnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.question_text', read_only=True)
    
    class Meta:
        model = Answer
        fields = ['id', 'question', 'question_text', 'selected_option', 'answer_text', 'is_correct', 'marks_obtained']

class QuizSubmissionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    
    class Meta:
        model = QuizSubmission
        fields = [
            'id', 'quiz', 'quiz_title', 'student', 'student_name', 'start_time',
            'end_time', 'marks_obtained', 'is_submitted', 'answers'
        ]
        read_only_fields = ['id', 'start_time', 'answers']
