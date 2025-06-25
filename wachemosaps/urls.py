from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.index, name='index'),
    path('signup' , views.signup, name='signup'),
    path('login', views.login, name='login'),
    path('about', views.about, name='about'),
    path('contact', views.contact, name='contact'),
    path('event', views.event, name='event'),
    path('features', views.features, name='features'),
    path('gallery', views.gallery, name='gallery'),
    path('news', views.news, name='news'),
    path('exams', views.exams, name='exams'),
    path('logout', auth_views.LogoutView.as_view(next_page='index',
         extra_context = {'no_cache': True}),  # Prevent caching on logout
         name='logout'  ),
     
    
]