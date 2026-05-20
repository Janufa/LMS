from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', LoginView.as_view(template_name='frontend/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/create/', views.course_create, name='course_create'),
    path('courses/<int:pk>/', views.course_detail, name='course_detail'),
    path('courses/<int:pk>/enroll/', views.course_enroll, name='course_enroll'),
    path('courses/<int:pk>/unenroll/', views.course_unenroll, name='course_unenroll'),
    path('attendance/', views.attendance, name='attendance'),
    path('announcements/', views.announcements, name='announcements'),
    path('assignments/', views.assignment_list, name='assignment_list'),
    path('profile/', views.profile, name='profile'),
]