from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='teacher_dashboard'),
    path('courses/', views.courses, name='teacher_courses'),
    path('courses/<int:course_id>/', views.course_detail, name='teacher_course_detail'),
    path('courses/<int:course_id>/gradebook/', views.gradebook, name='teacher_gradebook'),
    path('courses/<int:course_id>/attendance/', views.attendance_management, name='teacher_attendance'),
]
