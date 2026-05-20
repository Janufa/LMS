from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from announcements.models import Announcement
from assignments.models import Assignment, AssignmentSubmission
from courses.models import Course, Enrollment
from attendance.models import Attendance
from frontend.forms import AttendanceMarkForm as AttendanceForm, AnnouncementForm, CourseForm, RegistrationForm, AssignmentSubmissionForm, TeacherAttendanceForm
from users.models import CustomUser


@login_required
def home(request):
    recent_announcements = Announcement.objects.order_by('-created_at')[:5]
    if request.user.role == CustomUser.TEACHER:
        course_count = Course.objects.filter(instructor=request.user).count()
        student_count = Enrollment.objects.filter(course__instructor=request.user, status='active').count()
        context = {
            'course_count': course_count,
            'student_count': student_count,
            'recent_announcements': recent_announcements,
        }
    elif request.user.role == CustomUser.PARENT:
        children = request.user.children.select_related('student')[:5]
        context = {
            'children': children,
            'recent_announcements': recent_announcements,
        }
    elif request.user.role == CustomUser.ADMIN:
        total_users = CustomUser.objects.exclude(role=CustomUser.ADMIN).count()
        total_courses = Course.objects.count()
        active_enrollments = Enrollment.objects.filter(status='active').count()
        context = {
            'admin_stats': {
                'user_count': total_users,
                'course_count': total_courses,
                'active_enrollments': active_enrollments,
            },
            'recent_announcements': recent_announcements,
        }
    else:
        current_month_start = timezone.now().date().replace(day=1)
        monthly_attendance = Attendance.objects.filter(student=request.user, date__gte=current_month_start)
        attendance_total = monthly_attendance.count()
        present_count = monthly_attendance.filter(status='present').count()
        late_count = monthly_attendance.filter(status='late').count()
        absent_count = monthly_attendance.filter(status='absent').count()
        excused_count = monthly_attendance.filter(status='excused').count()
        attendance_rate = None
        if attendance_total:
            attendance_rate = round((present_count / attendance_total) * 100, 1)

        graded_submissions = AssignmentSubmission.objects.filter(
            student=request.user,
            submission_date__date__gte=current_month_start,
            marks_obtained__isnull=False
        )
        average_grade = None
        if graded_submissions.exists():
            total_percent = 0
            for submission in graded_submissions:
                if submission.assignment.total_marks:
                    total_percent += (submission.marks_obtained / submission.assignment.total_marks) * 100
            average_grade = round(total_percent / graded_submissions.count(), 1)

        recent_attendance = Attendance.objects.filter(student=request.user).order_by('-date')[:5]
        context = {
            'recent_attendance': recent_attendance,
            'active_courses': Course.objects.filter(enrollments__student=request.user, enrollments__status='active'),
            'recent_announcements': recent_announcements,
            'monthly_performance': {
                'attendance_rate': attendance_rate,
                'attendance_total': attendance_total,
                'present_count': present_count,
                'late_count': late_count,
                'absent_count': absent_count,
                'excused_count': excused_count,
                'average_grade': average_grade,
                'graded_submissions': graded_submissions.count(),
            },
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
    today = timezone.now().date()
    if request.user.role == CustomUser.TEACHER:
        selected_course = None
        course_id = request.GET.get('course')
        teacher_courses = Course.objects.filter(instructor=request.user, is_active=True)
        if course_id:
            selected_course = get_object_or_404(Course, pk=course_id, instructor=request.user)

        if request.method == 'POST':
            form = TeacherAttendanceForm(request.POST, request.FILES, user=request.user)
            if form.is_valid():
                cleaned = form.cleaned_data
                attendance, created = Attendance.objects.get_or_create(
                    student=cleaned['student'],
                    course=cleaned['course'],
                    date=today,
                    defaults={
                        'status': cleaned['status'],
                        'late_message': cleaned.get('late_message', ''),
                        'late_photo': cleaned.get('late_photo'),
                        'time_marked': timezone.now().time(),
                    }
                )
                if not created:
                    attendance.status = cleaned['status']
                    attendance.late_message = cleaned.get('late_message', '')
                    if cleaned.get('late_photo'):
                        attendance.late_photo = cleaned.get('late_photo')
                    attendance.time_marked = timezone.now().time()
                    attendance.save()
                messages.success(request, 'Attendance record saved.')
                return redirect('attendance')
        else:
            form = TeacherAttendanceForm(user=request.user, course=selected_course)

        enrollments = None
        attendance_rows = []
        if selected_course:
            enrollments = Enrollment.objects.filter(course=selected_course, status='active').select_related('student')
            today_records = Attendance.objects.filter(course=selected_course, date=today).select_related('student')
            attendance_by_student = {record.student_id: record for record in today_records}
            attendance_rows = [
                {
                    'student': enrollment.student,
                    'record': attendance_by_student.get(enrollment.student_id),
                }
                for enrollment in enrollments
            ]

        return render(request, 'frontend/attendance.html', {
            'teacher_history': Attendance.objects.filter(course__instructor=request.user).select_related('student', 'course').order_by('-date')[:30],
            'teacher_courses': teacher_courses,
            'selected_course': selected_course,
            'form': form,
            'enrollments': enrollments,
            'attendance_rows': attendance_rows,
            'today': today,
        })

    if request.method == 'POST':
        form = AttendanceForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            attendance, created = Attendance.objects.get_or_create(
                student=request.user,
                course=form.cleaned_data['course'],
                date=today,
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
    announcements = Announcement.objects.filter(is_published=True).order_by('-is_important', '-created_at')[:20]
    announcement_form = None
    if request.user.role == CustomUser.TEACHER:
        if request.method == 'POST':
            announcement_form = AnnouncementForm(request.POST, request.FILES, user=request.user)
            if announcement_form.is_valid():
                announcement = announcement_form.save(commit=False)
                announcement.posted_by = request.user
                announcement.save()
                messages.success(request, 'Announcement posted successfully.')
                return redirect('announcements')
        else:
            announcement_form = AnnouncementForm(user=request.user)
    return render(request, 'frontend/announcements.html', {
        'announcements': announcements,
        'announcement_form': announcement_form,
    })


@login_required
def assignment_list(request):
    if request.user.role == CustomUser.TEACHER:
        assignments = Assignment.objects.filter(course__instructor=request.user).order_by('due_date')
        submissions = AssignmentSubmission.objects.filter(assignment__course__instructor=request.user).select_related('student', 'assignment').order_by('-submission_date')
        assignment_items = [{'assignment': assignment, 'submission': None} for assignment in assignments]
        return render(request, 'frontend/assignments.html', {
            'assignment_items': assignment_items,
            'teacher_submissions': submissions,
        })

    assignments = Assignment.objects.filter(course__enrollments__student=request.user, course__enrollments__status='active').distinct().order_by('due_date')
    submissions = AssignmentSubmission.objects.filter(student=request.user).select_related('assignment').order_by('-submission_date')
    submission_map = {submission.assignment_id: submission for submission in submissions}
    assignment_items = []
    for assignment in assignments:
        assignment_items.append({
            'assignment': assignment,
            'submission': submission_map.get(assignment.id),
        })

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
        'assignment_items': assignment_items,
        'submissions': submissions,
        'submission_form': form,
    })
