from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='teacher_dashboard'),
    path('courses/', views.courses, name='teacher_courses'),
    path('courses/<int:course_id>/', views.course_detail, name='teacher_course_detail'),
    path('courses/<int:course_id>/gradebook/', views.gradebook, name='teacher_gradebook'),
    path('courses/<int:course_id>/attendance/', views.attendance_management, name='teacher_attendance'),
    path('gradebook/submission/<int:submission_id>/', views.grade_submission, name='teacher_grade_submission'),
    path('courses/<int:course_id>/attendance/mark/', views.mark_attendance, name='teacher_mark_attendance'),
    path('courses/<int:course_id>/assignment/create/', views.create_assignment, name='teacher_create_assignment'),
    path('courses/<int:course_id>/exam/create/', views.create_exam, name='teacher_create_exam'),
]


