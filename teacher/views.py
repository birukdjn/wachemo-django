from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.contrib.auth.models import User
from student.models import (
    Course, Student, Instructor, Department, Enrollment, Assignment, 
    AssignmentSubmission, Attendance, Exam, ExamResult, Announcement,
    TimetableSchedule, Message
)
from wachemosaps.decorators import teacher_required

@teacher_required
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

@teacher_required
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

@teacher_required
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

@teacher_required
def gradebook_overview(request):
    """
    Redirects to gradebook for the instructor's first course or courses list.
    """
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.warning(request, 'Instructor profile not found.')
        return redirect('teacher_dashboard')
    
    first_course = Course.objects.filter(instructor=instructor, is_active=True).first()
    if first_course:
        return redirect('teacher_gradebook', course_id=first_course.id)
    
    messages.info(request, 'No active courses assigned to view gradebook.')
    return redirect('teacher_courses')

@teacher_required
def attendance_overview(request):
    """
    Redirects to attendance management for the instructor's first course.
    """
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.warning(request, 'Instructor profile not found.')
        return redirect('teacher_dashboard')
    
    first_course = Course.objects.filter(instructor=instructor, is_active=True).first()
    if first_course:
        return redirect('teacher_attendance', course_id=first_course.id)
    
    messages.info(request, 'No active courses assigned to view attendance.')
    return redirect('teacher_courses')

@teacher_required
def gradebook(request, course_id):
    """
    Gradebook view for a specific course.
    """
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.warning(request, 'Instructor profile not found.')
        return redirect('teacher_dashboard')
    
    course = get_object_or_404(Course, id=course_id, instructor=instructor)
    all_courses = Course.objects.filter(instructor=instructor, is_active=True)

    
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
        'all_courses': all_courses,
        'enrollments': enrollments,
        'assignments': assignments,
        'submissions': submissions,
        'exam_results': exam_results,
    }
    return render(request, 'teacher/gradebook.html', context)

@teacher_required
def attendance_management(request, course_id):
    """
    Attendance management for a specific course.
    """
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.warning(request, 'Instructor profile not found.')
        return redirect('teacher_dashboard')
    
    course = get_object_or_404(Course, id=course_id, instructor=instructor)
    all_courses = Course.objects.filter(instructor=instructor, is_active=True)
    
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
        'all_courses': all_courses,
        'enrollments': enrollments,
        'attendance_records': attendance_records,
        'date_filter': date_filter,
    }
    return render(request, 'teacher/attendance_management.html', context)


@teacher_required
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


@teacher_required
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
                if Enrollment.objects.filter(student=student, course=course, is_active=True).exists():
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


@teacher_required
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


@teacher_required
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


@teacher_required
def teacher_profile(request):
    """
    Display and update instructor profile details.
    """
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.warning(request, 'Instructor profile not found.')
        return redirect('teacher_dashboard')
    
    user = request.user
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name).strip()
        user.last_name = request.POST.get('last_name', user.last_name).strip()
        user.email = request.POST.get('email', user.email).strip()
        user.save()

        instructor.phone = request.POST.get('phone', instructor.phone).strip()
        instructor.office_location = request.POST.get('office_location', instructor.office_location).strip()
        instructor.specialization = request.POST.get('specialization', instructor.specialization).strip()
        instructor.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('teacher_profile')

    context = {
        'instructor': instructor,
    }
    return render(request, 'teacher/profile.html', context)


@teacher_required
def teacher_timetable(request):
    """
    Weekly teaching timetable for the instructor.
    """
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.warning(request, 'Instructor profile not found.')
        return redirect('teacher_dashboard')

    schedules = TimetableSchedule.objects.filter(
        course__instructor=instructor
    ).select_related('course').order_by('start_time')

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    timetable_by_day = {day: [] for day in days}
    for item in schedules:
        if item.day_of_week in timetable_by_day:
            timetable_by_day[item.day_of_week].append(item)

    context = {
        'instructor': instructor,
        'schedules': schedules,
        'timetable_by_day': timetable_by_day,
        'days': days,
    }
    return render(request, 'teacher/timetable.html', context)


@teacher_required
def teacher_students(request):
    """
    Comprehensive student directory for the instructor's courses.
    """
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.warning(request, 'Instructor profile not found.')
        return redirect('teacher_dashboard')

    courses = Course.objects.filter(instructor=instructor, is_active=True)
    enrollments = Enrollment.objects.filter(
        course__instructor=instructor,
        is_active=True
    ).select_related('student__user', 'student__department', 'course')

    course_filter = request.GET.get('course')
    search_query = request.GET.get('search', '').strip()

    if course_filter:
        enrollments = enrollments.filter(course_id=course_filter)

    if search_query:
        enrollments = enrollments.filter(
            Q(student__user__first_name__icontains=search_query) |
            Q(student__user__last_name__icontains=search_query) |
            Q(student__student_id__icontains=search_query) |
            Q(student__user__email__icontains=search_query)
        )

    context = {
        'instructor': instructor,
        'courses': courses,
        'enrollments': enrollments,
        'course_filter': course_filter,
        'search_query': search_query,
    }
    return render(request, 'teacher/students.html', context)


@teacher_required
def teacher_exams(request):
    """
    Exams and assessments management view for instructors.
    """
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.warning(request, 'Instructor profile not found.')
        return redirect('teacher_dashboard')

    courses = Course.objects.filter(instructor=instructor, is_active=True)
    exams = Exam.objects.filter(course__instructor=instructor).select_related('course').order_by('-exam_date')
    exam_results = ExamResult.objects.filter(exam__course__instructor=instructor).select_related('student__user', 'exam')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'record_grade':
            exam_id = request.POST.get('exam_id')
            student_id = request.POST.get('student_id')
            points = request.POST.get('points_earned')
            feedback = request.POST.get('feedback', '')
            if exam_id and student_id and points is not None:
                exam_obj = get_object_or_404(Exam, id=exam_id, course__instructor=instructor)
                student_obj = get_object_or_404(Student, id=student_id)
                if not Enrollment.objects.filter(student=student_obj, course=exam_obj.course, is_active=True).exists():
                    messages.error(request, f'Student {student_obj.student_id} is not enrolled in this course.')
                    return redirect('teacher_exams')

                ExamResult.objects.update_or_create(
                    exam=exam_obj,
                    student=student_obj,
                    defaults={
                        'points_earned': int(points),
                        'feedback': feedback,
                        'is_published': True
                    }
                )
                messages.success(request, f'Recorded grade for {student_obj.get_full_name()}.')
                return redirect('teacher_exams')

    context = {
        'instructor': instructor,
        'courses': courses,
        'exams': exams,
        'exam_results': exam_results,
    }
    return render(request, 'teacher/exams.html', context)


@teacher_required
def teacher_announcements(request):
    """
    Create and manage instructor announcements.
    """
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.warning(request, 'Instructor profile not found.')
        return redirect('teacher_dashboard')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        priority = request.POST.get('priority', 'medium')
        target_audience = request.POST.get('target_audience', 'all')

        if title and content:
            Announcement.objects.create(
                title=title,
                content=content,
                priority=priority,
                target_audience=target_audience,
                department=instructor.department,
                is_published=True,
                created_by=request.user
            )
            messages.success(request, 'Announcement posted successfully!')
            return redirect('teacher_announcements')

    announcements = Announcement.objects.filter(
        Q(created_by=request.user) | Q(target_audience='all') | Q(target_audience='instructors')
    ).order_by('-publish_date')

    context = {
        'instructor': instructor,
        'announcements': announcements,
    }
    return render(request, 'teacher/announcements.html', context)


@teacher_required
def teacher_inbox(request):
    """
    Messaging system between teachers, students, and administration.
    """
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.warning(request, 'Instructor profile not found.')
        return redirect('teacher_dashboard')

    if request.method == 'POST':
        recipient_username = request.POST.get('recipient_username', '').strip()
        subject = request.POST.get('subject', '').strip()
        body = request.POST.get('body', '').strip()

        if recipient_username and subject and body:
            try:
                recipient_user = User.objects.get(username=recipient_username)
                Message.objects.create(
                    sender=request.user,
                    recipient=recipient_user,
                    subject=subject,
                    body=body
                )
                messages.success(request, f'Message sent to {recipient_user.username}!')
            except User.DoesNotExist:
                messages.error(request, f'User "{recipient_username}" not found.')
            return redirect('teacher_inbox')

    received_messages = Message.objects.filter(recipient=request.user).select_related('sender').order_by('-sent_at')
    sent_messages = Message.objects.filter(sender=request.user).select_related('recipient').order_by('-sent_at')

    enrolled_students = Student.objects.filter(
        enrollments__course__instructor=instructor,
        enrollments__is_active=True
    ).distinct().select_related('user')

    context = {
        'instructor': instructor,
        'received_messages': received_messages,
        'sent_messages': sent_messages,
        'enrolled_students': enrolled_students,
    }
    return render(request, 'teacher/inbox.html', context)




