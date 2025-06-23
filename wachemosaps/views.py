from django.shortcuts import render 
from .models import news



def index(request):
    # Fetch the latest news from the database
    latest_news = news.objects.all()
    return render(request, 'index.html' , {'news': latest_news})

def login(request):
    return render(request, 'login.html')
def signup(request):
    return render(request, 'signup.html')
