from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('event/', views.event, name='event'),
    path('features/', views.features, name='features'),
    path('gallery/', views.gallery, name='gallery'),
    path('news/', views.news, name='news'),
    path('exams/', views.exams, name='exams'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index',
         extra_context={'no_cache': True}), name='logout'),

    # Custom Admin Portal Routes
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/users/', views.admin_users, name='admin_users'),
    path('admin-dashboard/teachers/', views.admin_teachers, name='admin_teachers'),
    path('admin-dashboard/students/', views.admin_students, name='admin_students'),
    path('admin-dashboard/departments/', views.admin_departments, name='admin_departments'),
    path('admin-dashboard/courses/', views.admin_courses, name='admin_courses'),
    path('admin-dashboard/enrollments/', views.admin_enrollments, name='admin_enrollments'),
    path('admin-dashboard/assignments/', views.admin_assignments, name='admin_assignments'),
    path('admin-dashboard/timetables/', views.admin_timetables, name='admin_timetables'),
    path('admin-dashboard/exams/', views.admin_exams, name='admin_exams'),
    path('admin-dashboard/attendance/', views.admin_attendance, name='admin_attendance'),
    path('admin-dashboard/library/', views.admin_library, name='admin_library'),
    path('admin-dashboard/news/', views.admin_news, name='admin_news'),
    path('admin-dashboard/events/', views.admin_events, name='admin_events'),
    path('admin-dashboard/gallery/', views.admin_gallery, name='admin_gallery'),
    path('admin-dashboard/clubs/', views.admin_clubs, name='admin_clubs'),
    path('admin-dashboard/announcements/', views.admin_announcements, name='admin_announcements'),
    path('admin-dashboard/messages/', views.admin_messages, name='admin_messages'),

    # Fallback patterns without trailing slash
    path('signup', views.signup),
    path('login', views.login),
    path('about', views.about),
    path('contact', views.contact),
    path('event', views.event),
    path('features', views.features),
    path('gallery', views.gallery),
    path('news', views.news),
    path('exams', views.exams),
    path('logout', auth_views.LogoutView.as_view(next_page='index', extra_context={'no_cache': True})),
]