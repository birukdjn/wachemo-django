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


@login_required
def grade_submission(request, submission_id):
    """
    Grade a student assignment submission.
    """
    if request.method == 'POST':
        try:
            instructor = Instructor.objects.get(user=request.user)
        except Instructor.DoesNotExist:
            messages.warning(request, 'Instructor profile not found.')
            return redirect('teacher_dashboard')
        
        submission = get_object_or_404(AssignmentSubmission, id=submission_id, assignment__course__instructor=instructor)
        points = request.POST.get('points_earned')
        feedback = request.POST.get('feedback', '')
        
        if points is not None and points.strip() != '':
            submission.points_earned = int(points)
            submission.feedback = feedback
            submission.is_graded = True
            submission.save()
            messages.success(request, f'Grade saved for {submission.student.get_full_name()}.')
        return redirect('teacher_gradebook', course_id=submission.assignment.course.id)
    return redirect('teacher_dashboard')


@login_required
def mark_attendance(request, course_id):
    """
    Mark student attendance for a course date.
    """
    if request.method == 'POST':
        try:
            instructor = Instructor.objects.get(user=request.user)
        except Instructor.DoesNotExist:
            messages.warning(request, 'Instructor profile not found.')
            return redirect('teacher_dashboard')
        
        course = get_object_or_404(Course, id=course_id, instructor=instructor)
        attendance_date = request.POST.get('attendance_date', timezone.now().strftime('%Y-%m-%d'))
        student_ids = request.POST.getlist('student_ids')
        
        for sid in student_ids:
            status = request.POST.get(f'status_{sid}', 'present')
            try:
                student = Student.objects.get(id=sid)
                Attendance.objects.update_or_create(
                    student=student,
                    course=course,
                    date=attendance_date,
                    defaults={
                        'status': status,
                        'marked_by': instructor
                    }
                )
            except Student.DoesNotExist:
                continue
        
        messages.success(request, f'Attendance saved for {attendance_date}.')
        return redirect('teacher_attendance', course_id=course.id)
    return redirect('teacher_dashboard')


@login_required
def create_assignment(request, course_id):
    """
    Create a new assignment for a course.
    """
    if request.method == 'POST':
        instructor = get_object_or_404(Instructor, user=request.user)
        course = get_object_or_404(Course, id=course_id, instructor=instructor)
        
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        due_date_str = request.POST.get('due_date')
        max_points = int(request.POST.get('max_points', 100))
        is_published = request.POST.get('is_published') == 'on'
        
        if title and due_date_str:
            Assignment.objects.create(
                course=course,
                title=title,
                description=description,
                due_date=due_date_str,
                max_points=max_points,
                is_published=is_published
            )
            messages.success(request, f'Assignment "{title}" created successfully!')
        else:
            messages.error(request, 'Title and Due Date are required to create an assignment.')
            
    return redirect('teacher_course_detail', course_id=course_id)


@login_required
def create_exam(request, course_id):
    """
    Schedule a new exam for a course.
    """
    if request.method == 'POST':
        instructor = get_object_or_404(Instructor, user=request.user)
        course = get_object_or_404(Course, id=course_id, instructor=instructor)
        
        title = request.POST.get('title', '').strip()
        exam_type = request.POST.get('exam_type', 'midterm')
        description = request.POST.get('description', '').strip()
        exam_date_str = request.POST.get('exam_date')
        duration_minutes = int(request.POST.get('duration_minutes', 120))
        max_points = int(request.POST.get('max_points', 100))
        location = request.POST.get('location', '').strip()
        is_published = request.POST.get('is_published') == 'on'
        
        if title and exam_date_str:
            Exam.objects.create(
                course=course,
                title=title,
                exam_type=exam_type,
                description=description,
                exam_date=exam_date_str,
                duration_minutes=duration_minutes,
                max_points=max_points,
                location=location,
                is_published=is_published
            )
            messages.success(request, f'Exam "{title}" scheduled successfully!')
        else:
            messages.error(request, 'Title and Exam Date are required.')
            
    return redirect('teacher_course_detail', course_id=course_id)


