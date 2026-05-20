from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone

from users.models import CustomUser
from courses.models import Course
from assignments.models import Assignment, AssignmentSubmission
from attendance.models import Attendance
from announcements.models import Announcement


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    registration_number = forms.CharField(
        required=False,
        max_length=50,
        help_text='Only students need to enter a registration number.',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['registration_number'].required = False
        self.fields['registration_number'].widget.attrs.update({'class': 'form-control'})
        self.fields['role'].widget.attrs.update({'class': 'form-select'})
        for field_name in ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        registration_number = cleaned_data.get('registration_number')
        if role == CustomUser.STUDENT and not registration_number:
            self.add_error('registration_number', 'Registration number is required for student accounts.')
        return cleaned_data


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


class TeacherAttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['course', 'student', 'status', 'late_message', 'late_photo']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select'}),
            'student': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'late_message': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'late_photo': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        course = kwargs.pop('course', None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['course'].queryset = Course.objects.filter(instructor=user, is_active=True)
            self.fields['course'].widget.attrs.update({'class': 'form-select'})
        if course is not None:
            self.fields['student'].queryset = CustomUser.objects.filter(enrollments__course=course, enrollments__status='active', role=CustomUser.STUDENT).distinct()
        else:
            self.fields['student'].queryset = CustomUser.objects.filter(role=CustomUser.STUDENT)
        self.fields['student'].widget.attrs.update({'class': 'form-select'})
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


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['course', 'title', 'content', 'attachment', 'is_important', 'is_published']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
            'is_important': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['course'].queryset = Course.objects.filter(instructor=user)
            self.fields['course'].widget.attrs.update({'class': 'form-select'})
            self.fields['content'].widget.attrs.update({'class': 'form-control'})
            self.fields['attachment'].widget.attrs.update({'class': 'form-control'})
            self.fields['is_important'].required = False
            self.fields['is_published'].required = False


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
