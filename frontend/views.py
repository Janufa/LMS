from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from announcements.models import Announcement
from assignments.models import Assignment, AssignmentSubmission
from courses.models import Course, Enrollment
from attendance.models import Attendance
from frontend.forms import AttendanceMarkForm as AttendanceForm, CourseForm, RegistrationForm, AssignmentSubmissionForm
from users.models import CustomUser


@login_required
def home(request):
    if request.user.role == CustomUser.TEACHER:
        course_count = Course.objects.filter(instructor=request.user).count()
        student_count = Enrollment.objects.filter(course__instructor=request.user, status='active').count()
        context = {
            'course_count': course_count,
            'student_count': student_count,
            'recent_announcements': Announcement.objects.order_by('-created_at')[:5],
        }
    elif request.user.role == CustomUser.PARENT:
        children = request.user.children.select_related('student')[:5]
        context = {
            'children': children,
            'recent_announcements': Announcement.objects.order_by('-created_at')[:5],
        }
    else:
        recent_attendance = Attendance.objects.filter(student=request.user).order_by('-date')[:5]
        context = {
            'recent_attendance': recent_attendance,
            'active_courses': Course.objects.filter(enrollments__student=request.user, enrollments__status='active'),
            'recent_announcements': Announcement.objects.order_by('-created_at')[:5],
        }
    return render(request, 'frontend/home.html', context)


def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome! Your account has been created.')
            return redirect('home')
    else:
        form = RegistrationForm()
    return render(request, 'frontend/register.html', {'form': form})


@login_required
def profile(request):
    return render(request, 'frontend/profile.html')


@login_required
def course_list(request):
    courses = Course.objects.filter(is_active=True).order_by('title')
    if request.user.role == CustomUser.TEACHER:
        teacher_courses = Course.objects.filter(instructor=request.user)
    else:
        teacher_courses = None
    return render(request, 'frontend/course_list.html', {'courses': courses, 'teacher_courses': teacher_courses})


@login_required
def course_create(request):
    if request.user.role != CustomUser.TEACHER:
        messages.warning(request, 'Only teachers can create courses.')
        return redirect('course_list')
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            messages.success(request, 'Course created successfully.')
            return redirect('course_detail', pk=course.pk)
    else:
        form = CourseForm()
    return render(request, 'frontend/course_form.html', {'form': form})


@login_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    enrolled = Enrollment.objects.filter(course=course, student=request.user, status='active').exists()
    return render(request, 'frontend/course_detail.html', {'course': course, 'enrolled': enrolled})


@login_required
def course_enroll(request, pk):
    course = get_object_or_404(Course, pk=pk, is_active=True)
    Enrollment.objects.get_or_create(course=course, student=request.user, defaults={'status': 'active'})
    messages.success(request, f'Enrolled in {course.title}.')
    return redirect('course_detail', pk=pk)


@login_required
def course_unenroll(request, pk):
    course = get_object_or_404(Course, pk=pk)
    enrollment = Enrollment.objects.filter(course=course, student=request.user, status='active').first()
    if enrollment:
        enrollment.status = 'dropped'
        enrollment.save()
        messages.success(request, f'You have been unenrolled from {course.title}.')
    return redirect('course_detail', pk=pk)


@login_required
def attendance(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            attendance, created = Attendance.objects.get_or_create(
                student=request.user,
                course=form.cleaned_data['course'],
                date=timezone.now().date(),
                defaults={
                    'status': form.cleaned_data['status'],
                    'late_message': form.cleaned_data.get('late_message', ''),
                    'late_photo': form.cleaned_data.get('late_photo'),
                    'time_marked': timezone.now().time(),
                }
            )
            if not created:
                attendance.status = form.cleaned_data['status']
                attendance.late_message = form.cleaned_data.get('late_message', '')
                if form.cleaned_data.get('late_photo'):
                    attendance.late_photo = form.cleaned_data.get('late_photo')
                attendance.time_marked = timezone.now().time()
                attendance.save()
            messages.success(request, 'Attendance record saved.')
            return redirect('attendance')
    else:
        form = AttendanceForm(user=request.user)
    history = Attendance.objects.filter(student=request.user).order_by('-date')[:15]
    return render(request, 'frontend/attendance.html', {'form': form, 'history': history})


@login_required
def announcements(request):
    announcements = Announcement.objects.order_by('-created_at')[:20]
    return render(request, 'frontend/announcements.html', {'announcements': announcements})


@login_required
def assignment_list(request):
    assignments = Assignment.objects.filter(course__enrollments__student=request.user, course__enrollments__status='active').distinct()
    submissions = AssignmentSubmission.objects.filter(student=request.user)
    if request.method == 'POST':
        form = AssignmentSubmissionForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            submission, created = AssignmentSubmission.objects.get_or_create(
                assignment=form.cleaned_data['assignment'],
                student=request.user,
                defaults={
                    'submission_text': form.cleaned_data.get('submission_text', ''),
                    'submission_file': form.cleaned_data.get('submission_file'),
                    'status': 'submitted',
                }
            )
            if not created:
                submission.submission_text = form.cleaned_data.get('submission_text', '')
                if form.cleaned_data.get('submission_file'):
                    submission.submission_file = form.cleaned_data.get('submission_file')
                submission.status = 'submitted'
                submission.save()
            messages.success(request, 'Assignment submission saved successfully.')
            return redirect('assignment_list')
    else:
        form = AssignmentSubmissionForm(user=request.user)
    return render(request, 'frontend/assignments.html', {
        'assignments': assignments,
        'submissions': submissions,
        'submission_form': form,
    })
