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
    path('admin-dashboard/courses/', views.admin_courses, name='admin_courses'),

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