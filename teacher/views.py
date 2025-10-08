from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
from student.models import (
    Course, Student, Instructor, Department, Enrollment, Assignment, 
    AssignmentSubmission, Attendance, Exam, ExamResult, Announcement
)

@login_required
def dashboard(request):
    """
    Teacher dashboard with overview of courses and students.
    """
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.warning(request, 'Instructor profile not found.')
        return redirect('dashboard')
    
    # Get instructor's courses
    courses = Course.objects.filter(
        instructor=instructor,
        is_active=True
    ).select_related('department')
    
    # Get total students across all courses
    total_students = Enrollment.objects.filter(
        course__instructor=instructor,
        is_active=True
    ).values('student').distinct().count()
    
    # Get recent announcements
    announcements = Announcement.objects.filter(
        Q(target_audience='all') | Q(target_audience='instructors'),
        is_published=True,
        publish_date__lte=timezone.now()
    ).order_by('-publish_date')[:5]
    
    # Get pending assignments to grade
    pending_assignments = AssignmentSubmission.objects.filter(
        assignment__course__instructor=instructor,
        is_graded=False
    ).select_related('assignment', 'student__user')
    
    # Get upcoming exams
    upcoming_exams = Exam.objects.filter(
        course__instructor=instructor,
        exam_date__gte=timezone.now(),
        is_published=True
    ).order_by('exam_date')[:5]
    
    context = {
        'instructor': instructor,
        'courses': courses,
        'total_students': total_students,
        'announcements': announcements,
        'pending_assignments': pending_assignments,
        'upcoming_exams': upcoming_exams,
    }
    return render(request, 'teacher/dashboard.html', context)

@login_required
def courses(request):
    """
    Display instructor's courses with student lists.
    """
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.warning(request, 'Instructor profile not found.')
        return redirect('dashboard')
    
    courses = Course.objects.filter(
        instructor=instructor,
        is_active=True
    ).select_related('department').prefetch_related('enrollments__student__user')
    
    context = {
        'instructor': instructor,
        'courses': courses,
    }
    return render(request, 'teacher/courses.html', context)

@login_required
def course_detail(request, course_id):
    """
    Detailed view of a specific course with students and grades.
    """
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.warning(request, 'Instructor profile not found.')
        return redirect('dashboard')
    
    course = get_object_or_404(Course, id=course_id, instructor=instructor)
    
    # Get enrolled students
    enrollments = Enrollment.objects.filter(
        course=course,
        is_active=True
    ).select_related('student__user')
    
    # Get assignments for this course
    assignments = Assignment.objects.filter(course=course).order_by('-due_date')
    
    # Get exams for this course
    exams = Exam.objects.filter(course=course).order_by('-exam_date')
    
    # Get attendance summary
    attendance_summary = Attendance.objects.filter(
        course=course,
        date__gte=timezone.now() - timedelta(days=30)
    ).values('status').annotate(count=Count('status'))
    
    context = {
        'instructor': instructor,
        'course': course,
        'enrollments': enrollments,
        'assignments': assignments,
        'exams': exams,
        'attendance_summary': attendance_summary,
    }
    return render(request, 'teacher/course_detail.html', context)

@login_required
def gradebook(request, course_id):
    """
    Gradebook view for a specific course.
    """
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.warning(request, 'Instructor profile not found.')
        return redirect('dashboard')
    
    course = get_object_or_404(Course, id=course_id, instructor=instructor)
    
    # Get enrolled students
    enrollments = Enrollment.objects.filter(
        course=course,
        is_active=True
    ).select_related('student__user')
    
    # Get assignments
    assignments = Assignment.objects.filter(course=course).order_by('due_date')
    
    # Get assignment submissions
    submissions = AssignmentSubmission.objects.filter(
        assignment__course=course
    ).select_related('student__user', 'assignment')
    
    # Get exam results
    exam_results = ExamResult.objects.filter(
        exam__course=course
    ).select_related('student__user', 'exam')
    
    context = {
        'instructor': instructor,
        'course': course,
        'enrollments': enrollments,
        'assignments': assignments,
        'submissions': submissions,
        'exam_results': exam_results,
    }
    return render(request, 'teacher/gradebook.html', context)

@login_required
def attendance_management(request, course_id):
    """
    Attendance management for a specific course.
    """
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.warning(request, 'Instructor profile not found.')
        return redirect('dashboard')
    
    course = get_object_or_404(Course, id=course_id, instructor=instructor)
    
    # Get enrolled students
    enrollments = Enrollment.objects.filter(
        course=course,
        is_active=True
    ).select_related('student__user')
    
    # Get attendance records
    attendance_records = Attendance.objects.filter(
        course=course
    ).select_related('student__user').order_by('-date')
    
    # Filter by date if requested
    date_filter = request.GET.get('date')
    if date_filter:
        attendance_records = attendance_records.filter(date=date_filter)
    
    context = {
        'instructor': instructor,
        'course': course,
        'enrollments': enrollments,
        'attendance_records': attendance_records,
        'date_filter': date_filter,
    }
    return render(request, 'teacher/attendance_management.html', context)
