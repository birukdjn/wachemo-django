from django.shortcuts import render ,redirect
from .models import Course
from django.contrib.auth.decorators import login_required 
from datetime import datetime
from django.views.decorators.cache import cache_page
# Create your views here.

@login_required
def dashboard(request):
    current_month = datetime.now().month
    months = []
    for i in range(1, 13):
        months.append({
            'name': datetime(datetime.now().year, i, 1).strftime('%b'),
            'index': i-1,
            'is_current': i == current_month
        })
    courses = Course.objects.filter(is_active=True).select_related('instructor')
    total_courses = courses.count()
    featured_courses = courses.filter(is_featured=True) if hasattr(Course, 'is_featured') else []

    context = {
        'months': months,
        'courses': courses,
        'num_courses': total_courses,
        'featured_courses': featured_courses,
    }
    return render(request, 'student/dashboard.html', context )


@login_required
def courses(request):
    courses = Course.objects.filter(is_active=True).select_related('instructor')
    total_courses = courses.count()
    featured_courses = courses.filter(is_featured=True) if hasattr(Course, 'is_featured') else []

    context = {
        'courses': courses,
        'total_courses': total_courses,
        'featured_courses': featured_courses,
    }
    return render(request, 'student/courses.html', context)

@login_required
def attendance(request):
    """
    Display the attendance page for students.
    """
    return render(request, 'student/attendance.html')

@login_required
def support(request):
    return render(request, 'student/support.html')

@login_required
def settings(request):
    """
    Display the settings page for students.
    """
    return render(request, 'student/settings.html', {'active_section': 'settings'})

@login_required
def library(request):
    """
    Display the library page for students.
    """
    return render(request, 'student/library.html')