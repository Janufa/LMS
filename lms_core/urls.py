"""
URL configuration for lms project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.views.static import serve
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('', include('frontend.urls')),
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/users/', include('users.urls')),
    path('api/courses/', include('courses.urls')),
    path('api/materials/', include('materials.urls')),
    path('api/assignments/', include('assignments.urls')),
    path('api/quizzes/', include('quizzes.urls')),
    path('api/announcements/', include('announcements.urls')),
    path('api/attendance/', include('attendance.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    urlpatterns += [
        path('static/<path:path>', serve, {'document_root': settings.BASE_DIR / 'static'}),
    ]
