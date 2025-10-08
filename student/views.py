from django.shortcuts import render, redirect, get_object_or_404
from .models import (
    Course, Student, Instructor, Department, Enrollment, Assignment, 
    AssignmentSubmission, Attendance, Exam, ExamResult, Book, 
    BookBorrowing, Announcement, Notification
)
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from wachemosaps.models import UserProfile
# Create your views here.

@login_required
def dashboard(request):
    # Get student profile
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        student = None
    
    current_month = datetime.now().month
    months = []
    for i in range(1, 13):
        months.append({
            'name': datetime(datetime.now().year, i, 1).strftime('%b'),
            'index': i-1,
            'is_current': i == current_month
        })
    
    # Get student's enrolled courses
    if student:
        enrolled_courses = Course.objects.filter(
            enrollments__student=student,
            enrollments__is_active=True
        ).select_related('instructor', 'department')
        
        # Get recent announcements
        announcements = Announcement.objects.filter(
            Q(target_audience='all') | Q(target_audience='students'),
            is_published=True,
            publish_date__lte=timezone.now()
        ).order_by('-publish_date')[:5]
        
        # Get upcoming assignments
        upcoming_assignments = Assignment.objects.filter(
            course__in=enrolled_courses,
            due_date__gte=timezone.now(),
            is_published=True
        ).order_by('due_date')[:5]
        
        # Get upcoming exams
        upcoming_exams = Exam.objects.filter(
            course__in=enrolled_courses,
            exam_date__gte=timezone.now(),
            is_published=True
        ).order_by('exam_date')[:5]
        
        # Get attendance summary
        attendance_summary = Attendance.objects.filter(
            student=student,
            date__gte=timezone.now() - timedelta(days=30)
        ).values('status').annotate(count=Count('status'))
        
        # Get recent notifications
        notifications = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).order_by('-created_at')[:5]
        
    else:
        enrolled_courses = Course.objects.none()
        announcements = Announcement.objects.none()
        upcoming_assignments = Assignment.objects.none()
        upcoming_exams = Exam.objects.none()
        attendance_summary = []
        notifications = Notification.objects.none()

    # Get all active courses for general display
    all_courses = Course.objects.filter(is_active=True).select_related('instructor', 'department')
    total_courses = all_courses.count()
    featured_courses = all_courses.filter(is_featured=True)

    context = {
        'student': student,
        'months': months,
        'courses': enrolled_courses,
        'all_courses': all_courses,
        'num_courses': total_courses,
        'featured_courses': featured_courses,
        'announcements': announcements,
        'upcoming_assignments': upcoming_assignments,
        'upcoming_exams': upcoming_exams,
        'attendance_summary': attendance_summary,
        'notifications': notifications,
    }
    return render(request, 'student/dashboard.html', context)


@login_required
def courses(request):
    # Get student profile
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        student = None
    
    # Get all active courses
    courses = Course.objects.filter(is_active=True).select_related('instructor', 'department')
    total_courses = courses.count()
    featured_courses = courses.filter(is_featured=True)
    
    # Get student's enrolled courses
    enrolled_courses = []
    if student:
        enrolled_courses = Course.objects.filter(
            enrollments__student=student,
            enrollments__is_active=True
        ).select_related('instructor', 'department')
    
    # Get departments for filtering
    departments = Department.objects.filter(is_active=True)
    
    # Filter by department if requested
    department_filter = request.GET.get('department')
    if department_filter:
        courses = courses.filter(department_id=department_filter)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        courses = courses.filter(
            Q(name__icontains=search_query) | 
            Q(code__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    context = {
        'student': student,
        'courses': courses,
        'enrolled_courses': enrolled_courses,
        'total_courses': total_courses,
        'featured_courses': featured_courses,
        'departments': departments,
        'search_query': search_query,
        'department_filter': department_filter,
    }
    return render(request, 'student/courses.html', context)

@login_required
def attendance(request):
    """
    Display the attendance page for students.
    """
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        student = None
    
    if not student:
        messages.warning(request, 'Student profile not found.')
        return redirect('dashboard')
    
    # Get student's enrolled courses
    enrolled_courses = Course.objects.filter(
        enrollments__student=student,
        enrollments__is_active=True
    )
    
    # Get attendance records for the current semester
    current_semester = request.GET.get('semester', 'Fall 2024')
    attendance_records = Attendance.objects.filter(
        student=student,
        course__in=enrolled_courses
    ).select_related('course', 'marked_by__user').order_by('-date')
    
    # Filter by course if requested
    course_filter = request.GET.get('course')
    if course_filter:
        attendance_records = attendance_records.filter(course_id=course_filter)
    
    # Filter by date range if requested
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        attendance_records = attendance_records.filter(date__gte=date_from)
    if date_to:
        attendance_records = attendance_records.filter(date__lte=date_to)
    
    # Calculate attendance statistics
    total_classes = attendance_records.count()
    present_count = attendance_records.filter(status='present').count()
    absent_count = attendance_records.filter(status='absent').count()
    late_count = attendance_records.filter(status='late').count()
    excused_count = attendance_records.filter(status='excused').count()
    
    attendance_percentage = (present_count / total_classes * 100) if total_classes > 0 else 0
    
    # Get attendance by course
    attendance_by_course = []
    for course in enrolled_courses:
        course_attendance = attendance_records.filter(course=course)
        course_total = course_attendance.count()
        course_present = course_attendance.filter(status='present').count()
        course_percentage = (course_present / course_total * 100) if course_total > 0 else 0
        
        attendance_by_course.append({
            'course': course,
            'total': course_total,
            'present': course_present,
            'percentage': course_percentage
        })
    
    # Get recent attendance (last 30 days)
    recent_attendance = attendance_records.filter(
        date__gte=timezone.now() - timedelta(days=30)
    ).order_by('-date')[:20]
    
    context = {
        'student': student,
        'enrolled_courses': enrolled_courses,
        'attendance_records': attendance_records,
        'attendance_by_course': attendance_by_course,
        'recent_attendance': recent_attendance,
        'total_classes': total_classes,
        'present_count': present_count,
        'absent_count': absent_count,
        'late_count': late_count,
        'excused_count': excused_count,
        'attendance_percentage': attendance_percentage,
        'current_semester': current_semester,
        'course_filter': course_filter,
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'student/attendance.html', context)

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
    # Get student profile
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        student = None
    
    # Get books with search and filter functionality
    books = Book.objects.filter(is_active=True)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) | 
            Q(author__icontains=search_query) |
            Q(isbn__icontains=search_query)
        )
    
    # Category filter
    category_filter = request.GET.get('category')
    if category_filter:
        books = books.filter(category=category_filter)
    
    # Get student's borrowed books
    borrowed_books = []
    if student:
        borrowed_books = BookBorrowing.objects.filter(
            student=student,
            status__in=['borrowed', 'overdue']
        ).select_related('book')
    
    # Get library statistics
    total_books = Book.objects.filter(is_active=True).count()
    available_books = Book.objects.filter(is_active=True, available_copies__gt=0).count()
    borrowed_count = BookBorrowing.objects.filter(status='borrowed').count()
    
    context = {
        'student': student,
        'books': books,
        'borrowed_books': borrowed_books,
        'total_books': total_books,
        'available_books': available_books,
        'borrowed_count': borrowed_count,
        'search_query': search_query,
        'category_filter': category_filter,
    }
    return render(request, 'student/library.html', context)

@login_required
def assignments(request):
    """
    Display assignments for enrolled courses.
    """
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        student = None
    
    if not student:
        messages.warning(request, 'Student profile not found.')
        return redirect('dashboard')
    
    # Get student's enrolled courses
    enrolled_courses = Course.objects.filter(
        enrollments__student=student,
        enrollments__is_active=True
    )
    
    # Get assignments for enrolled courses
    assignments = Assignment.objects.filter(
        course__in=enrolled_courses,
        is_published=True
    ).select_related('course', 'course__instructor').order_by('-due_date')
    
    # Get student's submissions
    submissions = AssignmentSubmission.objects.filter(
        student=student
    ).select_related('assignment', 'assignment__course')
    
    context = {
        'student': student,
        'assignments': assignments,
        'submissions': submissions,
    }
    return render(request, 'student/assignments.html', context)

@login_required
def exams(request):
    """
    Display exams for enrolled courses.
    """
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        student = None
    
    if not student:
        messages.warning(request, 'Student profile not found.')
        return redirect('dashboard')
    
    # Get student's enrolled courses
    enrolled_courses = Course.objects.filter(
        enrollments__student=student,
        enrollments__is_active=True
    )
    
    # Get exams for enrolled courses
    exams = Exam.objects.filter(
        course__in=enrolled_courses,
        is_published=True
    ).select_related('course', 'course__instructor').order_by('exam_date')
    
    # Get student's exam results
    exam_results = ExamResult.objects.filter(
        student=student,
        is_published=True
    ).select_related('exam', 'exam__course')
    
    context = {
        'student': student,
        'exams': exams,
        'exam_results': exam_results,
    }
    return render(request, 'student/exams.html', context)

@login_required
def grades(request):
    """
    Display grades and academic progress.
    """
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        student = None
    
    if not student:
        messages.warning(request, 'Student profile not found.')
        return redirect('dashboard')
    
    # Get student's enrollments with grades
    enrollments = Enrollment.objects.filter(
        student=student,
        is_active=True
    ).select_related('course', 'course__instructor', 'course__department')
    
    # Get assignment grades
    assignment_grades = AssignmentSubmission.objects.filter(
        student=student,
        is_graded=True
    ).select_related('assignment', 'assignment__course')
    
    # Get exam grades
    exam_grades = ExamResult.objects.filter(
        student=student,
        is_published=True
    ).select_related('exam', 'exam__course')
    
    # Calculate GPA
    total_points = 0
    total_credits = 0
    for enrollment in enrollments:
        if enrollment.grade and enrollment.course.credits:
            # Convert grade to points (simplified)
            grade_points = {'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'F': 0.0}
            if enrollment.grade in grade_points:
                total_points += grade_points[enrollment.grade] * enrollment.course.credits
                total_credits += enrollment.course.credits
    
    calculated_gpa = total_points / total_credits if total_credits > 0 else 0
    
    context = {
        'student': student,
        'enrollments': enrollments,
        'assignment_grades': assignment_grades,
        'exam_grades': exam_grades,
        'calculated_gpa': calculated_gpa,
    }
    return render(request, 'student/grades.html', context)

@login_required
def profile(request):
    """
    Display the current user's profile and role info.
    """
    user: User = request.user
    user_profile = UserProfile.objects.filter(user=user).first()
    
    # Get student profile if exists
    try:
        student = Student.objects.get(user=user)
    except Student.DoesNotExist:
        student = None
    
    # Get instructor profile if exists
    try:
        instructor = Instructor.objects.get(user=user)
    except Instructor.DoesNotExist:
        instructor = None
    
    context = {
        'user': user,
        'profile': user_profile,
        'student': student,
        'instructor': instructor,
    }
    return render(request, 'student/profile.html', context)