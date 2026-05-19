from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Quiz, Question, Option, QuizSubmission, Answer
from .serializers import QuizSerializer, QuizDetailSerializer, QuestionSerializer, QuizSubmissionSerializer

class QuizViewSet(viewsets.ModelViewSet):
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['course', 'is_published']
    search_fields = ['title', 'description']
    ordering_fields = ['start_date', 'created_at']
    ordering = ['-start_date']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Quiz.objects.all()
        elif user.is_teacher:
            return Quiz.objects.filter(course__instructor=user)
        else:
            return Quiz.objects.filter(
                course__enrollments__student=user,
                course__enrollments__status='active',
                is_published=True
            ).distinct()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return QuizDetailSerializer
        return QuizSerializer
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def start_quiz(self, request, pk=None):
        """Start a quiz"""
        quiz = self.get_object()
        student = request.user
        
        if student.role != 'student':
            return Response(
                {'error': 'Only students can take quizzes.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        now = timezone.now()
        if now < quiz.start_date or now > quiz.end_date:
            return Response(
                {'error': 'Quiz is not available at this time.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        submission, created = QuizSubmission.objects.get_or_create(
            quiz=quiz,
            student=student,
            defaults={'start_time': now}
        )
        
        serializer = QuizSubmissionSerializer(submission)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def submit_quiz(self, request, pk=None):
        """Submit quiz answers"""
        quiz = self.get_object()
        student = request.user
        
        try:
            submission = QuizSubmission.objects.get(quiz=quiz, student=student)
        except QuizSubmission.DoesNotExist:
            return Response(
                {'error': 'Quiz submission not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if submission.is_submitted:
            return Response(
                {'error': 'Quiz already submitted.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Process answers
        answers_data = request.data.get('answers', [])
        total_marks = 0
        
        for answer_data in answers_data:
            question_id = answer_data.get('question_id')
            selected_option_id = answer_data.get('selected_option_id')
            answer_text = answer_data.get('answer_text', '')
            
            try:
                question = Question.objects.get(id=question_id)
                answer = Answer.objects.create(
                    submission=submission,
                    question=question,
                    answer_text=answer_text
                )
                
                if selected_option_id:
                    answer.selected_option_id = selected_option_id
                    try:
                        option = Option.objects.get(id=selected_option_id)
                        answer.is_correct = option.is_correct
                        if option.is_correct:
                            answer.marks_obtained = question.marks
                            total_marks += question.marks
                    except Option.DoesNotExist:
                        pass
                
                answer.save()
            except Question.DoesNotExist:
                continue
        
        submission.end_time = timezone.now()
        submission.is_submitted = True
        submission.marks_obtained = total_marks
        submission.save()
        
        serializer = QuizSubmissionSerializer(submission)
        return Response(serializer.data)

class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['quiz']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Question.objects.all()
        elif user.is_teacher:
            return Question.objects.filter(quiz__course__instructor=user)
        else:
            return Question.objects.filter(
                quiz__course__enrollments__student=user,
                quiz__course__enrollments__status='active',
                quiz__is_published=True
            ).distinct()
