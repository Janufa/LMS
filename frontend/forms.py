from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone

from users.models import CustomUser
from courses.models import Course
from assignments.models import Assignment, AssignmentSubmission
from attendance.models import Attendance


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'registration_number',
            'password1',
            'password2',
        ]


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            'title',
            'code',
            'description',
            'credits',
            'max_students',
            'start_date',
            'end_date',
            'is_active',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class AttendanceMarkForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['course', 'status', 'late_message', 'late_photo']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'late_message': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['course'].queryset = Course.objects.filter(enrollments__student=user, enrollments__status='active')
            self.fields['course'].widget.attrs.update({'class': 'form-select'})
            self.fields['late_photo'].widget.attrs.update({'class': 'form-control'})
            self.fields['late_message'].required = False
            self.fields['late_photo'].required = False

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        late_message = cleaned_data.get('late_message')
        late_photo = cleaned_data.get('late_photo')
        if status == 'late' and not late_message and not late_photo:
            raise forms.ValidationError('Provide either a late reason or upload proof when marking late.')
        return cleaned_data


class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['assignment', 'submission_text', 'submission_file']
        widgets = {
            'assignment': forms.Select(attrs={'class': 'form-select'}),
            'submission_text': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'submission_file': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['assignment'].queryset = Assignment.objects.filter(course__enrollments__student=user, course__enrollments__status='active').distinct()
        self.fields['submission_text'].required = False
