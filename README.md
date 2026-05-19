# Learning Management System (LMS)

A comprehensive Django-based Learning Management System built with Django REST Framework for managing online learning activities.

## Features

- **User Management**: Admin, Teacher, Student, and Parent roles
- **Course Management**: Create and manage courses with enrollment system
- **Study Materials**: Upload and manage study materials (PDF, Video, Documents)
- **Assignments**: Create assignments and track submissions with grading
- **Quizzes**: Create interactive quizzes with MCQ and short answer questions
- **Attendance Tracking**: Automatic attendance marking after 8:30 AM with late arrival photo/message requirement
- **Parent Portal**: Parents can view their children's attendance and academic progress
- **Announcements**: Course announcements with read tracking
- **API Documentation**: Swagger UI for API exploration

## Tech Stack

- **Backend**: Django 4.2.10
- **API**: Django REST Framework 3.14.0
- **Database**: SQLite (default) / MySQL
- **Authentication**: Token-based authentication
- **Documentation**: drf-spectacular

## Installation

### Prerequisites
- Python 3.8+
- pip
- Virtual Environment (recommended)

### Setup Steps

1. **Clone/Extract the project**
```bash
cd lms
```

2. **Create Virtual Environment**
```bash
python -m venv venv
```

3. **Activate Virtual Environment**
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

4. **Install Dependencies**
```bash
pip install -r requirements.txt
```

5. **Configure Environment**
```bash
# Create .env file from example
copy .env.example .env

# Edit .env with your settings (if needed)
```

6. **Run Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

7. **Create Superuser (Admin)**
```bash
python manage.py createsuperuser
```

8. **Collect Static Files** (Optional, for production)
```bash
python manage.py collectstatic --noinput
```

9. **Run Development Server**
```bash
python manage.py runserver
```

The server will be available at `http://localhost:8000`

## Usage

### Access Points

- **Admin Panel**: http://localhost:8000/admin/
- **API Documentation**: http://localhost:8000/api/docs/
- **API Schema**: http://localhost:8000/api/schema/

### Automatic Attendance Marking

To automatically mark students absent after 8:30 AM, run the management command:

```bash
python manage.py mark_absent_after_830
```

**Scheduling (for production):**
Use celery beat or cron jobs to run this command daily at 8:31 AM:

```bash
# Linux/macOS cron
31 8 * * * cd /path/to/lms && /path/to/venv/bin/python manage.py mark_absent_after_830
```

## API Endpoints

### Authentication
- `POST /api/users/` - Register new user
- `GET /api/users/me/` - Get current user profile

### Courses
- `GET /api/courses/` - List all courses
- `POST /api/courses/` - Create course (teacher/admin only)
- `POST /api/courses/{id}/enroll/` - Enroll in course
- `GET /api/courses/{id}/students/` - List enrolled students
- `GET /api/courses/my_courses/` - Get my courses

### Materials
- `GET /api/materials/` - List study materials
- `POST /api/materials/` - Upload material (teacher/admin only)

### Assignments
- `GET /api/assignments/` - List assignments
- `POST /api/assignments/` - Create assignment (teacher/admin only)
- `POST /api/assignments/submissions/` - Submit assignment
- `POST /api/assignments/submissions/{id}/grade/` - Grade submission (teacher/admin only)

### Quizzes
- `GET /api/quizzes/` - List quizzes
- `POST /api/quizzes/{id}/start_quiz/` - Start quiz
- `POST /api/quizzes/{id}/submit_quiz/` - Submit quiz

### Attendance
- `POST /api/attendance/mark_present/` - Mark attendance
- `GET /api/attendance/student_attendance_history/` - View attendance history
- `GET /api/attendance/children_attendance/` - View children's attendance (parent only)
- `POST /api/attendance/{id}/approve_late/` - Approve late arrival (teacher/admin only)

### Announcements
- `GET /api/announcements/` - List announcements
- `POST /api/announcements/` - Post announcement (teacher/admin only)
- `POST /api/announcements/{id}/mark_as_read/` - Mark as read

## User Roles

### Student
- View and enroll in courses
- Submit assignments
- Take quizzes
- Mark attendance
- View announcements
- Check grades

### Teacher
- Create and manage courses
- Upload study materials
- Create assignments and quizzes
- Grade submissions
- Manage announcements
- Track student attendance

### Parent
- View child's attendance
- View child's academic progress
- Receive notifications

### Admin
- Full system access
- Manage all users
- Manage all courses and content

## Late Arrival Policy

- Students must mark attendance **before 8:30 AM** to be marked present
- After 8:30 AM, they must provide:
  - **Message**: Explanation for late arrival
  - **Photo**: Proof/selfie at the time
- Teachers can approve or reject late arrivals
- Approved late arrivals are marked as "Excused"
- Rejected late arrivals are marked as "Absent"

## Database Schema

### Key Models
- **CustomUser**: Extended Django user with roles
- **Course**: Course information with instructor
- **Enrollment**: Student enrollment in courses
- **StudyMaterial**: Learning materials for courses
- **Assignment**: Course assignments
- **AssignmentSubmission**: Student submissions with grading
- **Attendance**: Student attendance records
- **Quiz**: Quiz information and questions
- **Announcement**: Course announcements
- **ParentStudent**: Parent-child relationships

## Configuration

### Settings File
Edit `lms_core/settings.py` for:
- Database settings
- Email configuration
- Security settings
- Logging preferences

### Environment Variables (.env)
```
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_NAME=lms_db
DATABASE_USER=root
DATABASE_PASSWORD=password
DATABASE_HOST=localhost
DATABASE_PORT=3306
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Troubleshooting

### Migration Issues
```bash
# Reset migrations (careful - deletes data)
python manage.py migrate courses zero
python manage.py migrate
```

### Static Files Not Loading
```bash
python manage.py collectstatic --clear --noinput
```

### Permission Denied
Ensure user has appropriate role for the action they're trying to perform.

## Development

### Running Tests
```bash
python manage.py test
```

### Code Style
Use the following for code formatting:
```bash
# Install dev dependencies
pip install black flake8

# Format code
black .

# Check style
flake8 .
```

## Deployment

For production deployment:
1. Set `DEBUG=False` in settings
2. Configure allowed hosts
3. Use a production-grade database (PostgreSQL)
4. Set secure secret key
5. Use HTTPS
6. Configure static/media file serving
7. Use production WSGI server (Gunicorn)

## Support

For issues or questions, please refer to Django and Django REST Framework documentation:
- [Django Docs](https://docs.djangoproject.com/)
- [DRF Docs](https://www.django-rest-framework.org/)

## License

This project is open source and available under the MIT License.

## Contributing

1. Fork the repository
2. Create feature branch
3. Make your changes
4. Submit pull request

---

**Last Updated**: May 2026
