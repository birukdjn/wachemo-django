from django.shortcuts import render , redirect
from .models import News,  Gallery, Event
from django.contrib import messages
from django.contrib.auth.models import User, auth, Permission
from django.views.decorators.cache import cache_page
from django.contrib.auth import login as auth_login
from .models import UserProfile





def index(request):
    context= {
        'topnews': News.objects.all().order_by('-date')[:3],  # Get the latest 3 news items
        'topimages': Gallery.objects.all().order_by('-id')[:8],  # Get the latest 8 images
        'topevents': Event.objects.all().order_by('-day', '-month')[:4],  # Get the latest 4 events
    }
    return render(request, 'index.html', context)

@cache_page(60*60)  # Cache for 1 hour
def about(request):
    return render(request, 'about.html')

@cache_page(60*60)  # Cache for 1 hour
def contact(request):
    return render(request, 'contact.html')

@cache_page(60*60)     # Cache for 1 hour
def features(request):
    return render(request, 'features.html')


def news(request):
    allnews = News.objects.all().order_by('-date')
    context = {
        'allnews': allnews
    }
    return render(request, 'news.html', context) 

@cache_page(60*60)  # Cache for 1 hour
def event(request):
    events= Event.objects.all().order_by('-day', '-month')
    context = {
        'events': events
    }
    return render(request, 'event.html', context)

@cache_page(60*60)  # Cache for 1 hour
def gallery(request):
    context = {
        'allimages': Gallery.objects.all()  
    }
    return render(request, 'gallery.html' , context)

@cache_page(60*60)  # Cache for 1 hour
def exams(request):
    return render(request, 'exams.html')


    
def signup(request):
    if request.method == 'POST':
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST['role']
        confirm_password = request.POST['confirm_password']
        
        # Validation checks
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('signup')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('signup')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('signup')
        
        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=firstname,
                last_name=lastname
            )
            
            # Create user profile with role
            UserProfile.objects.create(
                user=user,
                role=role,
                student_id=request.POST.get('student_id', '') if role == 'student' else None,
                teacher_subject=request.POST.get('teacher_subject', '') if role == 'teacher' else None,
                parent_phone=request.POST.get('parent_phone', '') if role == 'parent' else None
            )
            
            messages.success(request, ' Account created successfully! Please log in.')
            return redirect('login')
            
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return redirect('signup')     
    return render(request, 'signup.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)
        if user is None:
            messages.error(request, 'Invalid credentials. Please try again.')
            return redirect('login')

        # Get user role from UserProfile
        user_profile = UserProfile.objects.filter(user=user).first()
        role = user_profile.role if user_profile else None

        auth_login(request, user)

        if user.is_staff:
            return redirect('/admin/')
        elif role == 'student':
            return redirect('dashboard')
        else:
            return redirect('index')
        
    else:
        return render(request, 'login.html')
    
