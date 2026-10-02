from django.shortcuts import render , redirect
from .models import News,  Gallery, Event
from django.contrib import messages
from django.contrib.auth.models import User, auth, Permission
from django.contrib.auth import login as auth_login
from .models import UserProfile





from student.models import Student, Instructor, Course, Announcement

def index(request):
    context = {
        'topnews': News.objects.all().order_by('-date')[:3],  # Get the latest 3 news items
        'topimages': Gallery.objects.all().order_by('-id')[:8],  # Get the latest 8 images
        'topevents': Event.objects.all().order_by('-day', '-month')[:4],  # Get the latest 4 events
        'announcements': Announcement.objects.filter(is_published=True).order_by('-publish_date')[:3],
        'student_count': Student.objects.count(),
        'instructor_count': Instructor.objects.count(),
        'course_count': Course.objects.count(),
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
    events= Event.objects.all().order_by('-day', '-month')
    context = {
        'events': events
    }
    return render(request, 'event.html', context)


def gallery(request):
    context = {
        'allimages': Gallery.objects.all().order_by('-id')  
    }
    return render(request, 'gallery.html' , context)

def exams(request):
    return render(request, 'exams.html')


    
from student.models import Student, Instructor

def signup(request):
    if request.method == 'POST':
        firstname = request.POST.get('firstname', '')
        lastname = request.POST.get('lastname', '')
        email = request.POST.get('email', '')
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        role = request.POST.get('role', 'student')
        confirm_password = request.POST.get('confirm_password', '')
        
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
            
            # Get or create user profile with role
            user_profile, _ = UserProfile.objects.get_or_create(user=user)
            user_profile.role = role
            user_profile.student_id = request.POST.get('student_id', '') if role == 'student' else None
            user_profile.teacher_subject = request.POST.get('teacher_subject', '') if role == 'teacher' else None
            user_profile.parent_phone = request.POST.get('parent_phone', '') if role == 'parent' else None
            user_profile.save()
            
            # Auto-create Student / Instructor records if applicable
            if role == 'student':
                sid = user_profile.student_id or f"WCU/{user.id:04d}"
                Student.objects.get_or_create(user=user, defaults={'student_id': sid})
            elif role == 'teacher':
                eid = f"EMP/{user.id:04d}"
                Instructor.objects.get_or_create(user=user, defaults={'employee_id': eid, 'specialization': user_profile.teacher_subject or ''})
            
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
            
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return redirect('signup')     
    return render(request, 'signup.html')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        user = auth.authenticate(username=username, password=password)
        if user is None:
            messages.error(request, 'Invalid credentials. Please try again.')
            return redirect('login')

        # Get or create user profile
        user_profile, _ = UserProfile.objects.get_or_create(user=user, defaults={'role': 'student'})
        role = user_profile.role

        auth_login(request, user)

        if user.is_staff:
            return redirect('/admin/')
        elif role == 'teacher':
            Instructor.objects.get_or_create(user=user, defaults={'employee_id': f"EMP/{user.id:04d}"})
            return redirect('teacher_dashboard')
        elif role == 'student':
            Student.objects.get_or_create(user=user, defaults={'student_id': f"WCU/{user.id:04d}"})
            return redirect('dashboard')
        else:
            return redirect('index')
        
    else:
        return render(request, 'login.html')

    
