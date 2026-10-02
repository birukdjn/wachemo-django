from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from wachemosaps.models import UserProfile
from student.models import Instructor, Student

def teacher_required(view_func):
    """
    Strict isolation decorator for Teacher Portal (/teacher/).
    ONLY active Teacher accounts can view /teacher/*.
    Admins are redirected to /admin/, Students to /student/.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        # System Administrators must use the Admin Panel
        if request.user.is_superuser or request.user.is_staff:
            messages.error(request, "Access Restricted: System Administrators must use the Admin Control Panel.")
            return redirect('/admin/')

        user_profile, _ = UserProfile.objects.get_or_create(user=request.user, defaults={'role': 'student'})
        user_role = user_profile.role

        if user_role == 'teacher':
            Instructor.objects.get_or_create(
                user=request.user,
                defaults={'employee_id': f"EMP/{request.user.id:04d}", 'specialization': user_profile.teacher_subject or 'Faculty'}
            )
            return view_func(request, *args, **kwargs)

        # Non-teachers are blocked and redirected to their assigned dashboard
        messages.error(request, "Access Denied: You do not have permission to view the Teacher Portal.")
        if user_role == 'student':
            return redirect('dashboard')
        else:
            return redirect('index')

    return _wrapped_view


def student_required(view_func):
    """
    Strict isolation decorator for Student Portal (/student/).
    ONLY active Student accounts can view /student/*.
    Admins are redirected to /admin/, Teachers to /teacher/.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        # System Administrators must use the Admin Panel
        if request.user.is_superuser or request.user.is_staff:
            messages.error(request, "Access Restricted: System Administrators must use the Admin Control Panel.")
            return redirect('/admin/')

        user_profile, _ = UserProfile.objects.get_or_create(user=request.user, defaults={'role': 'student'})
        user_role = user_profile.role

        if user_role == 'student':
            Student.objects.get_or_create(
                user=request.user,
                defaults={'student_id': user_profile.student_id or f"STU/{request.user.id:04d}"}
            )
            return view_func(request, *args, **kwargs)

        # Non-students are blocked and redirected to their assigned dashboard
        messages.error(request, "Access Denied: You do not have permission to view the Student Portal.")
        if user_role == 'teacher':
            return redirect('teacher_dashboard')
        else:
            return redirect('index')

    return _wrapped_view


def admin_required(view_func):
    """
    Strict isolation decorator for Admin routes.
    ONLY Superusers/Staff can access Admin routes.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.is_superuser or request.user.is_staff:
            return view_func(request, *args, **kwargs)

        user_profile, _ = UserProfile.objects.get_or_create(user=request.user, defaults={'role': 'student'})
        user_role = user_profile.role

        messages.error(request, "Access Denied: Administrator privileges required.")
        if user_role == 'teacher':
            return redirect('teacher_dashboard')
        elif user_role == 'student':
            return redirect('dashboard')
        else:
            return redirect('index')

    return _wrapped_view


def parent_required(view_func):
    """
    Strict isolation decorator for Parent Portal (/parent/).
    ONLY active Parent accounts (or admins) can access Parent views.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
            
        user_profile, _ = UserProfile.objects.get_or_create(user=request.user, defaults={'role': 'parent'})
        user_role = user_profile.role

        if user_role == 'parent' or request.user.is_superuser or request.user.is_staff:
            return view_func(request, *args, **kwargs)

        messages.error(request, "Access Denied: You do not have permission to access the Parent Portal.")
        if user_role == 'teacher':
            return redirect('teacher_dashboard')
        elif user_role == 'student':
            return redirect('dashboard')
        else:
            return redirect('index')

    return _wrapped_view

