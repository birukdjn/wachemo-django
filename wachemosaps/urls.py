from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('gallery/', views.gallery, name='gallery'),
    path('blog/', views.blog, name='blog'),
    path('faq/', views.faq, name='faq'),
    path('signup' , views.signup, name='signup'),
    path('login', views.login, name='login'),
    path('testimonials/', views.testimonials, name='testimonials'),
    path('events/', views.events, name='events'),
    path('news/', views.news, name='news'),
 ]