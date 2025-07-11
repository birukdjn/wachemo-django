from django.urls import path
from . import views




urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('courses/', views.courses, name='courses'),
    path('attendance/', views.attendance, name='attendance'),
    path('support/', views.support, name='support'),
    path('settings/', views.settings, name='settings'),
    path('library/', views.library, name='library'),
    

]

