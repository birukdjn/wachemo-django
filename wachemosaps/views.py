from django.shortcuts import render , redirect
from .models import News,  Gallery
from django.contrib import messages
from django.contrib.auth.models import User, auth 




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
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid credentials. Please try again.')
            return redirect('login')
    else:
        return render(request, 'login.html')

def signup(request):
    if request.method == 'POST':
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password != confirm_password:
            messages.info(request, 'Passwords do not match.')
            return redirect('signup')
        elif User.objects.filter(username=username).exists():
            messages.info(request, 'Username already exists.')
            return redirect('signup')
        elif User.objects.filter(email=email).exists():
            messages.info(request, 'Email already exists.')
            return redirect('signup')
        else:
            user = User.objects.create_user(
                username=username,
                password=password,
                email = email,
                first_name=firstname,
                last_name=lastname,
            )
            user.save()
            messages.success(request, 'Account created successfully!')
            return redirect('login')
    else:
        messages.info(request, 'Please fill out the form to sign up.')
        return render(request, 'signup.html')
    