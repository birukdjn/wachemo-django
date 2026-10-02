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
        
        # Cyber Security & Governance Policy: Faculty accounts cannot be self-created publicly
        if role == 'teacher':
            messages.error(request, 'Security Notice: Faculty and Teacher accounts are provisioned exclusively by School Administration & Registrar. Please contact the Academic Office.')
            return redirect('signup')
        
        # Restrict public self-registration role to student or parent
        if role not in ['student', 'parent']:
            role = 'student'

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
            user_profile.parent_phone = request.POST.get('parent_phone', '') if role == 'parent' else None
            user_profile.save()
            
            # Auto-create Student record for self-registered student
            if role == 'student':
                sid = user_profile.student_id or f"WCU/{user.id:04d}"
                Student.objects.get_or_create(user=user, defaults={'student_id': sid})
            
            messages.success(request, 'Student account registered successfully! Please log in.')
            return redirect('login')
            
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return redirect('signup')     
    return render(request, 'signup.html')

from wachemosaps.decorators import admin_required
from student.models import Student, Instructor, Course, Announcement, Department
from django.db.models import Q

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

        if user.is_staff or user.is_superuser:
            return redirect('admin_dashboard')
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


# Custom Admin Dashboard Views
@admin_required
def admin_dashboard(request):
    """
    Custom Admin Control Panel with system statistics and governance overview.
    """
    student_count = Student.objects.count()
    instructor_count = Instructor.objects.count()
    course_count = Course.objects.count()
    department_count = Department.objects.count()
    user_count = User.objects.count()
    
    recent_users = User.objects.select_related('userprofile').order_by('-date_joined')[:8]
    recent_courses = Course.objects.select_related('instructor', 'department').order_by('-created_at')[:5]

    context = {
        'student_count': student_count,
        'instructor_count': instructor_count,
        'course_count': course_count,
        'department_count': department_count,
        'user_count': user_count,
        'recent_users': recent_users,
        'recent_courses': recent_courses,
    }
    return render(request, 'admin_portal/dashboard.html', context)


@admin_required
def admin_users(request):
    """
    Admin user governance and role assignment.
    """
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        new_role = request.POST.get('role')
        if user_id and new_role:
            target_user = get_object_or_404(User, id=user_id)
            profile, _ = UserProfile.objects.get_or_create(user=target_user)
            profile.role = new_role
            profile.save()

            if new_role == 'teacher':
                Instructor.objects.get_or_create(user=target_user, defaults={'employee_id': f"EMP/{target_user.id:04d}"})
            elif new_role == 'student':
                Student.objects.get_or_create(user=target_user, defaults={'student_id': f"WCU/{target_user.id:04d}"})

            messages.success(request, f'Updated role for {target_user.username} to {new_role.capitalize()}.')
            return redirect('admin_users')

    role_filter = request.GET.get('role', '')
    search_query = request.GET.get('search', '').strip()

    users = User.objects.select_related('userprofile').order_by('-date_joined')
    if role_filter:
        users = users.filter(userprofile__role=role_filter)
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    context = {
        'users': users,
        'role_filter': role_filter,
        'search_query': search_query,
    }
    return render(request, 'admin_portal/users.html', context)


@admin_required
def admin_teachers(request):
    """
    Manage instructors and faculty provisioning.
    """
    if request.method == 'POST':
        firstname = request.POST.get('firstname', '').strip()
        lastname = request.POST.get('lastname', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        department_id = request.POST.get('department_id')
        specialization = request.POST.get('specialization', '').strip()

        if username and password:
            if User.objects.filter(username=username).exists():
                messages.error(request, f'Username "{username}" already exists.')
            else:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                    first_name=firstname,
                    last_name=lastname
                )
                profile, _ = UserProfile.objects.get_or_create(user=user)
                profile.role = 'teacher'
                profile.save()

                dept = Department.objects.filter(id=department_id).first() if department_id else None
                Instructor.objects.create(
                    user=user,
                    employee_id=f"EMP/{user.id:04d}",
                    department=dept,
                    specialization=specialization
                )
                messages.success(request, f'Teacher profile created for {username}!')
                return redirect('admin_teachers')

    teachers = Instructor.objects.select_related('user', 'department').order_by('-created_at')
    departments = Department.objects.filter(is_active=True)

    context = {
        'teachers': teachers,
        'departments': departments,
    }
    return render(request, 'admin_portal/teachers.html', context)


@admin_required
def admin_students(request):
    """
    Manage student registry and academic records.
    """
    if request.method == 'POST':
        firstname = request.POST.get('firstname', '').strip()
        lastname = request.POST.get('lastname', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        department_id = request.POST.get('department_id')
        gpa = request.POST.get('gpa')

        if username and password:
            if User.objects.filter(username=username).exists():
                messages.error(request, f'Username "{username}" already exists.')
            else:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                    first_name=firstname,
                    last_name=lastname
                )
                profile, _ = UserProfile.objects.get_or_create(user=user)
                profile.role = 'student'
                profile.save()

                dept = Department.objects.filter(id=department_id).first() if department_id else None
                Student.objects.create(
                    user=user,
                    student_id=f"WCU/{user.id:04d}",
                    department=dept,
                    gpa=float(gpa) if gpa else None
                )
                messages.success(request, f'Student profile created for {username}!')
                return redirect('admin_students')

    students = Student.objects.select_related('user', 'department').order_by('-created_at')
    departments = Department.objects.filter(is_active=True)

    context = {
        'students': students,
        'departments': departments,
    }
    return render(request, 'admin_portal/students.html', context)


@admin_required
def admin_courses(request):
    """
    Manage courses and instructor assignments.
    """
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        instructor_id = request.POST.get('instructor_id')
        department_id = request.POST.get('department_id')
        credits_num = request.POST.get('credits', 3)

        if code and name:
            if Course.objects.filter(code=code).exists():
                messages.error(request, f'Course code "{code}" already exists.')
            else:
                instructor = Instructor.objects.filter(id=instructor_id).first() if instructor_id else None
                dept = Department.objects.filter(id=department_id).first() if department_id else None

                Course.objects.create(
                    code=code,
                    name=name,
                    description=description,
                    instructor=instructor,
                    department=dept,
                    credits=int(credits_num),
                    is_active=True
                )
                messages.success(request, f'Course "{code} - {name}" created successfully!')
                return redirect('admin_courses')

    courses = Course.objects.select_related('instructor__user', 'department').order_by('-created_at')
    instructors = Instructor.objects.select_related('user')
    departments = Department.objects.filter(is_active=True)

    context = {
        'courses': courses,
        'instructors': instructors,
        'departments': departments,
    }
    return render(request, 'admin_portal/courses.html', context)


    
