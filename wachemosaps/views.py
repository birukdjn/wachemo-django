from django.shortcuts import render 
from .models import news



def index(request):
    # Fetch the latest news from the database
    latest_news = news.objects.all()
    return render(request, 'index.html' , {'news': latest_news})

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def event(request):
    return render(request, 'event.html')

def login(request):
    return render(request, 'login.html')

def signup(request):
    return render(request, 'signup.html')
