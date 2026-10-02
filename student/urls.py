from django.urls import path
from . import views


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('courses/', views.courses, name='courses'),
    path('courses/enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('attendance/', views.attendance, name='attendance'),
    path('assignments/', views.assignments, name='assignments'),
    path('assignments/submit/<int:assignment_id>/', views.submit_assignment, name='submit_assignment'),
    path('exams/', views.exams, name='exams'),
    path('grades/', views.grades, name='grades'),
    path('support/', views.support, name='support'),
    path('settings/', views.settings, name='settings'),
    path('library/', views.library, name='library'),
    path('library/borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('profile/', views.profile, name='student_profile'),
    # New Features
    path('timetable/', views.timetable, name='timetable'),
    path('inbox/', views.inbox, name='inbox'),
    path('inbox/send/', views.send_message_view, name='send_message'),
    path('inbox/read/<int:message_id>/', views.read_message, name='read_message'),
    path('clubs/', views.clubs, name='clubs'),
    path('clubs/join/<int:club_id>/', views.join_club, name='join_club'),
    path('notifications/read/<int:notif_id>/', views.mark_notification_read, name='mark_notification_read'),
]
