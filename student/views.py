from django.shortcuts import render ,redirect
# Create your views here.


def dashboard(request):
    """
    Render the student dashboard page.
    """
    return render(request, 'student/dashboard.html')


def courses(request):
    return  redirect('course')