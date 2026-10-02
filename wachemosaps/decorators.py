from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from wachemosaps.models import UserProfile
from student.models import Instructor, Student

def role_required(allowed_roles=None):
    """
    Decorator for views that checks if the user has one of the allowed roles,
    or is a superuser/staff member.
    """
    if allowed_roles is None:
        allowed_roles = []

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            # Superusers and Staff always have full administrative access across all portals
            if request.user.is_superuser or request.user.is_staff:
                # Ensure Instructor / Student object exists on the fly if needed for admin testing
                if 'teacher' in allowed_roles:
                    Instructor.objects.get_or_create(
                        user=request.user,
                        defaults={'employee_id': f"EMP/{request.user.id:04d}", 'specialization': 'Administration'}
                    )
                if 'student' in allowed_roles:
                    Student.objects.get_or_create(
                        user=request.user,
                        defaults={'student_id': f"STU/{request.user.id:04d}"}
                    )
                return view_func(request, *args, **kwargs)

            # Check user role via UserProfile
            user_profile, _ = UserProfile.objects.get_or_create(user=request.user, defaults={'role': 'student'})
            user_role = user_profile.role

            if user_role in allowed_roles:
                if user_role == 'teacher':
                    Instructor.objects.get_or_create(
                        user=request.user,
                        defaults={'employee_id': f"EMP/{request.user.id:04d}", 'specialization': user_profile.teacher_subject or 'Faculty'}
                    )
                elif user_role == 'student':
                    Student.objects.get_or_create(
                        user=request.user,
                        defaults={'student_id': user_profile.student_id or f"STU/{request.user.id:04d}"}
                    )
                return view_func(request, *args, **kwargs)
            
            # Unauthorized role access handling
            messages.error(
                request, 
                f"Access Denied: Your account role ('{user_role.title()}') does not have permission to view this section."
            )

            # Redirect based on user's actual role
            if user_role == 'teacher':
                return redirect('teacher_dashboard')
            elif user_role == 'student':
                return redirect('dashboard')
            elif user_role == 'parent':
                return redirect('index')
            else:
                return redirect('index')

        return _wrapped_view
    return decorator


def teacher_required(view_func):
    """Decorator ensuring only Teachers or Superusers/Staff can access faculty routes."""
    return role_required(allowed_roles=['teacher'])(view_func)


def student_required(view_func):
    """Decorator ensuring only Students or Superusers/Staff can access student routes."""
    return role_required(allowed_roles=['student'])(view_func)


def admin_required(view_func):
    """Decorator ensuring only Superusers/Staff can access administrative routes."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.is_superuser or request.user.is_staff:
            return view_func(request, *args, **kwargs)
        messages.error(request, "Access Denied: Administrator privileges required.")
        return redirect('index')
    return _wrapped_view
