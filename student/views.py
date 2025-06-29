from django.shortcuts import render ,redirect
from .models import Course
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def dashboard(request):
     courses = Course.objects.filter(is_active=True).select_related('instructor')
     total_courses = courses.count()
     featured_courses = courses.filter(is_featured=True) if hasattr(Course, 'is_featured') else []

     context = {
        'courses': courses,
        'num_courses': total_courses,
        'featured_courses': featured_courses,
    }
     return render(request, 'student/dashboard.html', context )


@login_required
def courses(request):
    """
    Display a list of active courses with their instructors and other important details.
    """
    courses = Course.objects.filter(is_active=True).select_related('instructor')
    total_courses = courses.count()
    featured_courses = courses.filter(is_featured=True) if hasattr(Course, 'is_featured') else []

    context = {
        'courses': courses,
        'total_courses': total_courses,
        'featured_courses': featured_courses,
    }
    return redirect('courses', context)