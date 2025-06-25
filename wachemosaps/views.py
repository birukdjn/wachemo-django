from django.shortcuts import render 
from .models import News,  Gallery



def index(request):
    context= {
        'topnews': News.objects.all().order_by('-date')[:3],  # Get the latest 3 news items
        'topimages': Gallery.objects.all().order_by('-id')[:8],  # Get the latest 8 images
    }
    return render(request, 'index.html', context)

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def features(request):
    return render(request, 'features.html')

def news(request):
    allnews = News.objects.all().order_by('-date')
    context = {
        'allnews': allnews
    }
    return render(request, 'news.html', context) 

def event(request):
    return render(request, 'event.html')

def gallery(request):
    context = {
        'allimages': Gallery.objects.all()  
    }
    return render(request, 'gallery.html' , context)

def exams(request):
    return render(request, 'exams.html')

def login(request):
    return render(request, 'login.html')

def signup(request):
    return render(request, 'signup.html')
