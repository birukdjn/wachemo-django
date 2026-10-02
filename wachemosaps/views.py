from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Count, Avg
from django.contrib import messages
from django.contrib.auth.models import User, auth, Permission
from django.contrib.auth import login as auth_login
from .models import News, Gallery, Event, UserProfile
from .decorators import admin_required, parent_required

from student.models import (
    Department, Instructor, Student, Course, Enrollment,
    Assignment, AssignmentSubmission, Attendance, Exam, ExamResult,
    Book, BookBorrowing, Announcement, Notification, TimetableSchedule,
    Message, StudentClub, ClubMembership
)

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
        elif role == 'parent':
            return redirect('parent_dashboard')
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


@admin_required
def admin_departments(request):
    """
    Manage departments and academic faculties.
    """
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            name = request.POST.get('name', '').strip()
            code = request.POST.get('code', '').strip().upper()
            description = request.POST.get('description', '').strip()
            if name and code:
                if Department.objects.filter(Q(code=code) | Q(name=name)).exists():
                    messages.error(request, 'Department code or name already exists.')
                else:
                    Department.objects.create(name=name, code=code, description=description)
                    messages.success(request, f'Department "{code} - {name}" created successfully!')
                    return redirect('admin_departments')
        elif action == 'toggle':
            dept_id = request.POST.get('dept_id')
            dept = get_object_or_404(Department, id=dept_id)
            dept.is_active = not dept.is_active
            dept.save()
            messages.success(request, f'Status updated for {dept.name}.')
            return redirect('admin_departments')

    departments = Department.objects.annotate(
        student_count=Count('students', distinct=True),
        instructor_count=Count('instructors', distinct=True),
        course_count=Count('courses', distinct=True)
    ).order_by('code')

    context = {'departments': departments}
    return render(request, 'admin_portal/departments.html', context)


@admin_required
def admin_enrollments(request):
    """
    Manage student course enrollments and grading.
    """
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'enroll':
            student_id = request.POST.get('student_id')
            course_id = request.POST.get('course_id')
            semester = request.POST.get('semester', 'Fall 2026')
            academic_year = request.POST.get('academic_year', '2025/2026')

            student = get_object_or_404(Student, id=student_id)
            course = get_object_or_404(Course, id=course_id)

            enrollment, created = Enrollment.objects.get_or_create(
                student=student,
                course=course,
                semester=semester,
                academic_year=academic_year
            )
            if created:
                messages.success(request, f'Enrolled {student.student_id} in {course.code}.')
            else:
                messages.info(request, f'{student.student_id} is already enrolled in {course.code}.')
            return redirect('admin_enrollments')

        elif action == 'update_grade':
            messages.error(request, "Security Policy Violation: Administrators are restricted to read-only grade access. Only assigned faculty instructors can award or edit student grades.")
            return redirect('admin_enrollments')

    enrollments = Enrollment.objects.select_related('student__user', 'course').order_by('-enrollment_date')
    students = Student.objects.select_related('user').filter(status='active')
    courses = Course.objects.filter(is_active=True)

    context = {
        'enrollments': enrollments,
        'students': students,
        'courses': courses,
    }
    return render(request, 'admin_portal/enrollments.html', context)


@admin_required
def admin_assignments(request):
    """
    Manage course assignments and student submissions.
    """
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create_assignment':
            course_id = request.POST.get('course_id')
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '').strip()
            due_date = request.POST.get('due_date')
            max_points = request.POST.get('max_points', 100)
            is_published = request.POST.get('is_published') == 'on'

            course = get_object_or_404(Course, id=course_id)
            Assignment.objects.create(
                course=course,
                title=title,
                description=description,
                due_date=due_date,
                max_points=int(max_points),
                is_published=is_published
            )
            messages.success(request, f'Assignment "{title}" created for {course.code}.')
            return redirect('admin_assignments')

        elif action == 'grade_submission':
            messages.error(request, "Security Policy Violation: Administrators are restricted to read-only submission access. Only assigned faculty instructors can grade student submissions.")
            return redirect('admin_assignments')

    assignments = Assignment.objects.select_related('course').order_by('-created_at')
    submissions = AssignmentSubmission.objects.select_related('assignment__course', 'student__user').order_by('-submitted_at')
    courses = Course.objects.filter(is_active=True)

    context = {
        'assignments': assignments,
        'submissions': submissions,
        'courses': courses,
    }
    return render(request, 'admin_portal/assignments.html', context)


@admin_required
def admin_timetables(request):
    """
    Manage class timetable schedules across all courses.
    """
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        day_of_week = request.POST.get('day_of_week')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        room = request.POST.get('room', 'Hall A').strip()

        if course_id and day_of_week and start_time and end_time:
            course = get_object_or_404(Course, id=course_id)
            TimetableSchedule.objects.create(
                course=course,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time,
                room=room
            )
            messages.success(request, f'Schedule added for {course.code} on {day_of_week}.')
            return redirect('admin_timetables')

    schedules = TimetableSchedule.objects.select_related('course__instructor__user').order_by('day_of_week', 'start_time')
    courses = Course.objects.filter(is_active=True)

    context = {
        'schedules': schedules,
        'courses': courses,
    }
    return render(request, 'admin_portal/timetables.html', context)


@admin_required
def admin_exams(request):
    """
    Manage examination schedules and result entries.
    """
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create_exam':
            course_id = request.POST.get('course_id')
            title = request.POST.get('title', '').strip()
            exam_type = request.POST.get('exam_type', 'midterm')
            exam_date = request.POST.get('exam_date')
            duration = request.POST.get('duration_minutes', 120)
            max_points = request.POST.get('max_points', 100)
            location = request.POST.get('location', '').strip()

            course = get_object_or_404(Course, id=course_id)
            Exam.objects.create(
                course=course,
                title=title,
                exam_type=exam_type,
                exam_date=exam_date,
                duration_minutes=int(duration),
                max_points=int(max_points),
                location=location,
                is_published=True
            )
            messages.success(request, f'Exam "{title}" created for {course.code}.')
            return redirect('admin_exams')

        elif action == 'add_result':
            messages.error(request, "Security Policy Violation: Administrators are restricted to read-only exam scorecard access. Only assigned faculty instructors can enter exam marks.")
            return redirect('admin_exams')

    exams = Exam.objects.select_related('course').order_by('-exam_date')
    results = ExamResult.objects.select_related('exam__course', 'student__user').order_by('-created_at')
    courses = Course.objects.filter(is_active=True)
    students = Student.objects.filter(status='active')

    context = {
        'exams': exams,
        'results': results,
        'courses': courses,
        'students': students,
    }
    return render(request, 'admin_portal/exams.html', context)


@admin_required
def admin_attendance(request):
    """
    Audit and log student attendance.
    """
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        course_id = request.POST.get('course_id')
        date = request.POST.get('date')
        status = request.POST.get('status', 'present')
        notes = request.POST.get('notes', '').strip()

        student = get_object_or_404(Student, id=student_id)
        course = get_object_or_404(Course, id=course_id)

        Attendance.objects.update_or_create(
            student=student,
            course=course,
            date=date,
            defaults={'status': status, 'notes': notes}
        )
        messages.success(request, f'Attendance logged for {student.student_id} on {date}.')
        return redirect('admin_attendance')

    attendance_records = Attendance.objects.select_related('student__user', 'course').order_by('-date')
    students = Student.objects.filter(status='active')
    courses = Course.objects.filter(is_active=True)

    context = {
        'attendance_records': attendance_records,
        'students': students,
        'courses': courses,
    }
    return render(request, 'admin_portal/attendance.html', context)


@admin_required
def admin_library(request):
    """
    Manage school library collection and borrowing logs.
    """
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_book':
            title = request.POST.get('title', '').strip()
            author = request.POST.get('author', '').strip()
            isbn = request.POST.get('isbn', '').strip()
            category = request.POST.get('category', 'textbook')
            total_copies = request.POST.get('total_copies', 1)
            location = request.POST.get('location', '').strip()

            Book.objects.create(
                title=title,
                author=author,
                isbn=isbn,
                category=category,
                total_copies=int(total_copies),
                available_copies=int(total_copies),
                location=location
            )
            messages.success(request, f'Book "{title}" added to library.')
            return redirect('admin_library')

        elif action == 'issue_book':
            book_id = request.POST.get('book_id')
            student_id = request.POST.get('student_id')
            due_date = request.POST.get('due_date')

            book = get_object_or_404(Book, id=book_id)
            student = get_object_or_404(Student, id=student_id)

            if book.available_copies > 0:
                BookBorrowing.objects.create(
                    book=book,
                    student=student,
                    due_date=due_date,
                    status='borrowed'
                )
                book.available_copies -= 1
                book.save()
                messages.success(request, f'Book "{book.title}" issued to {student.student_id}.')
            else:
                messages.error(request, f'No copies available for "{book.title}".')
            return redirect('admin_library')

    books = Book.objects.filter(is_active=True).order_by('-created_at')
    borrowings = BookBorrowing.objects.select_related('book', 'student__user').order_by('-borrowed_date')
    students = Student.objects.filter(status='active')

    context = {
        'books': books,
        'borrowings': borrowings,
        'students': students,
    }
    return render(request, 'admin_portal/library.html', context)


@admin_required
def admin_news(request):
    """
    Manage news articles and campus press.
    """
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            title = request.POST.get('title', '').strip()
            content = request.POST.get('content', '').strip()
            reporter = request.POST.get('reporter', '').strip()
            image = request.POST.get('image', '').strip()
            day = request.POST.get('day', 1)
            month = request.POST.get('month', 'Jan')

            News.objects.create(
                title=title,
                content=content,
                reporter=reporter,
                image=image if image else None,
                day=int(day),
                month=month
            )
            messages.success(request, f'News article "{title}" published!')
            return redirect('admin_news')
        elif action == 'delete':
            news_id = request.POST.get('news_id')
            News.objects.filter(id=news_id).delete()
            messages.success(request, 'News article removed.')
            return redirect('admin_news')

    news_items = News.objects.all().order_by('-date')
    context = {'news_items': news_items}
    return render(request, 'admin_portal/news.html', context)


@admin_required
def admin_events(request):
    """
    Manage campus events and schedules.
    """
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '').strip()
            location = request.POST.get('location', '').strip()
            duration = request.POST.get('duration', '').strip()
            day = request.POST.get('day', 1)
            month = request.POST.get('month', 'Jan')

            Event.objects.create(
                title=title,
                description=description,
                location=location,
                duration=duration,
                day=int(day),
                month=month
            )
            messages.success(request, f'Event "{title}" scheduled!')
            return redirect('admin_events')
        elif action == 'delete':
            event_id = request.POST.get('event_id')
            Event.objects.filter(id=event_id).delete()
            messages.success(request, 'Event removed.')
            return redirect('admin_events')

    events = Event.objects.all().order_by('-id')
    context = {'events': events}
    return render(request, 'admin_portal/events.html', context)


@admin_required
def admin_gallery(request):
    """
    Manage gallery media uploads supporting local file uploads and image URLs.
    """
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            description = request.POST.get('description', '').strip()
            image_source = request.POST.get('image_source', 'file')
            image_file = request.FILES.get('image_file')
            image_url = request.POST.get('image_url', '').strip()

            if image_source == 'file' and image_file:
                gallery = Gallery.objects.create(
                    image_file=image_file,
                    description=description
                )
                gallery.image = gallery.image_file.url
                gallery.save(update_fields=['image'])
                messages.success(request, 'Gallery image uploaded from local storage successfully.')
                return redirect('admin_gallery')
            elif image_url:
                Gallery.objects.create(
                    image_url=image_url,
                    image=image_url,
                    description=description
                )
                messages.success(request, 'Gallery image added from URL link successfully.')
                return redirect('admin_gallery')
            elif image_file:
                gallery = Gallery.objects.create(
                    image_file=image_file,
                    description=description
                )
                gallery.image = gallery.image_file.url
                gallery.save(update_fields=['image'])
                messages.success(request, 'Gallery image uploaded from local storage successfully.')
                return redirect('admin_gallery')
            else:
                messages.error(request, 'Please select an image file to upload or provide a valid image URL.')
                return redirect('admin_gallery')
        elif action == 'delete':
            gallery_id = request.POST.get('gallery_id')
            Gallery.objects.filter(id=gallery_id).delete()
            messages.success(request, 'Gallery item removed.')
            return redirect('admin_gallery')

    gallery_items = Gallery.objects.all().order_by('-id')
    context = {'gallery_items': gallery_items}
    return render(request, 'admin_portal/gallery.html', context)


@admin_required
def admin_clubs(request):
    """
    Manage student clubs and memberships.
    """
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create_club':
            name = request.POST.get('name', '').strip()
            category = request.POST.get('category', 'Academic').strip()
            description = request.POST.get('description', '').strip()
            advisor_id = request.POST.get('advisor_id')

            advisor = Instructor.objects.filter(id=advisor_id).first() if advisor_id else None
            StudentClub.objects.create(
                name=name,
                category=category,
                description=description,
                advisor=advisor
            )
            messages.success(request, f'Club "{name}" created successfully.')
            return redirect('admin_clubs')

        elif action == 'add_member':
            club_id = request.POST.get('club_id')
            student_id = request.POST.get('student_id')
            role = request.POST.get('role', 'Member')

            club = get_object_or_404(StudentClub, id=club_id)
            student = get_object_or_404(Student, id=student_id)

            ClubMembership.objects.get_or_create(
                club=club,
                student=student,
                defaults={'role': role}
            )
            messages.success(request, f'Added {student.student_id} to {club.name}.')
            return redirect('admin_clubs')

    clubs = StudentClub.objects.annotate(member_count=Count('memberships')).order_by('-created_at')
    memberships = ClubMembership.objects.select_related('club', 'student__user').order_by('-joined_date')
    instructors = Instructor.objects.select_related('user')
    students = Student.objects.filter(status='active')

    context = {
        'clubs': clubs,
        'memberships': memberships,
        'instructors': instructors,
        'students': students,
    }
    return render(request, 'admin_portal/clubs.html', context)


@admin_required
def admin_announcements(request):
    """
    Manage portal-wide broadcasts and announcements.
    """
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            title = request.POST.get('title', '').strip()
            content = request.POST.get('content', '').strip()
            priority = request.POST.get('priority', 'medium')
            target_audience = request.POST.get('target_audience', 'all')

            Announcement.objects.create(
                title=title,
                content=content,
                priority=priority,
                target_audience=target_audience,
                is_published=True,
                created_by=request.user
            )
            messages.success(request, f'Announcement "{title}" published!')
            return redirect('admin_announcements')
        elif action == 'delete':
            ann_id = request.POST.get('announcement_id')
            Announcement.objects.filter(id=ann_id).delete()
            messages.success(request, 'Announcement removed.')
            return redirect('admin_announcements')

    announcements = Announcement.objects.select_related('created_by').order_by('-created_at')
    context = {'announcements': announcements}
    return render(request, 'admin_portal/announcements.html', context)


@admin_required
def admin_messages(request):
    """
    Manage system messaging and support communication.
    """
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient_id')
        subject = request.POST.get('subject', '').strip()
        body = request.POST.get('body', '').strip()

        if recipient_id and subject and body:
            recipient = get_object_or_404(User, id=recipient_id)
            Message.objects.create(
                sender=request.user,
                recipient=recipient,
                subject=subject,
                body=body
            )
            messages.success(request, f'Message sent to {recipient.username}.')
            return redirect('admin_messages')

    user_messages = Message.objects.select_related('sender', 'recipient').order_by('-sent_at')[:30]
    users = User.objects.exclude(id=request.user.id).order_by('username')

    context = {
        'messages_list': user_messages,
        'users': users,
    }
    return render(request, 'admin_portal/messages.html', context)


# ============================================================
# PARENT PORTAL VIEWS
# ============================================================

def _get_parent_student(request):
    """
    Helper to get active child for the logged in parent.
    Never auto-links arbitrary students to unlinked parents.
    """
    children = Student.objects.filter(parent=request.user).select_related('user', 'department')
    
    selected_child_id = request.GET.get('child_id')
    selected_child = None
    if selected_child_id:
        selected_child = children.filter(id=selected_child_id).first()
        if not selected_child:
            selected_child = children.first()
    else:
        selected_child = children.first()
    return children, selected_child


@parent_required
def parent_dashboard(request):
    """
    Main Parent Portal Dashboard overviewing child's academic performance.
    """
    children, child = _get_parent_student(request)
    
    enrollments = []
    attendance_records = []
    exam_results = []
    assignments = []
    attendance_percent = 100
    
    if child:
        enrollments = Enrollment.objects.filter(student=child).select_related('course__instructor__user')
        attendance_records = Attendance.objects.filter(student=child).select_related('course').order_by('-date')[:10]
        total_att = Attendance.objects.filter(student=child).count()
        present_att = Attendance.objects.filter(student=child, status='present').count()
        if total_att > 0:
            attendance_percent = round((present_att / total_att) * 100, 1)

        exam_results = ExamResult.objects.filter(student=child).select_related('exam__course').order_by('-created_at')[:5]
        assignments = AssignmentSubmission.objects.filter(student=child).select_related('assignment__course').order_by('-submitted_at')[:5]

    announcements = Announcement.objects.filter(is_published=True).order_by('-created_at')[:4]
    user_messages = Message.objects.filter(recipient=request.user).select_related('sender').order_by('-sent_at')[:4]

    context = {
        'children': children,
        'child': child,
        'enrollments': enrollments,
        'attendance_records': attendance_records,
        'attendance_percent': attendance_percent,
        'exam_results': exam_results,
        'assignments': assignments,
        'announcements': announcements,
        'messages_list': user_messages,
    }
    return render(request, 'parent/dashboard.html', context)


@parent_required
def parent_children(request):
    """
    Manage linked children / students.
    """
    if request.method == 'POST':
        student_id_input = request.POST.get('student_id', '').strip()
        if student_id_input:
            student = Student.objects.filter(Q(student_id__iexact=student_id_input) | Q(user__username__iexact=student_id_input)).first()
            if student:
                student.parent = request.user
                student.save()
                messages.success(request, f'Successfully linked {student.get_full_name()} ({student.student_id}) to your parent account!')
            else:
                messages.error(request, f'No student found with ID/Username "{student_id_input}". Please verify with school registrar.')
            return redirect('parent_children')

    children = Student.objects.filter(parent=request.user).select_related('user', 'department')
    context = {'children': children}
    return render(request, 'parent/children.html', context)


@parent_required
def parent_attendance(request):
    """
    Detailed attendance history and audit for parent's child.
    """
    children, child = _get_parent_student(request)
    attendance_records = []
    stats = {'present': 0, 'absent': 0, 'late': 0, 'excused': 0, 'total': 0, 'percent': 100}

    if child:
        attendance_records = Attendance.objects.filter(student=child).select_related('course', 'marked_by__user').order_by('-date')
        stats['total'] = attendance_records.count()
        stats['present'] = attendance_records.filter(status='present').count()
        stats['absent'] = attendance_records.filter(status='absent').count()
        stats['late'] = attendance_records.filter(status='late').count()
        stats['excused'] = attendance_records.filter(status='excused').count()
        if stats['total'] > 0:
            stats['percent'] = round((stats['present'] / stats['total']) * 100, 1)

    context = {
        'children': children,
        'child': child,
        'attendance_records': attendance_records,
        'stats': stats,
    }
    return render(request, 'parent/attendance.html', context)


@parent_required
def parent_grades(request):
    """
    Academic report card, course grades, and exam scores.
    """
    children, child = _get_parent_student(request)
    enrollments = []
    exam_results = []
    submissions = []

    if child:
        enrollments = Enrollment.objects.filter(student=child).select_related('course__department')
        exam_results = ExamResult.objects.filter(student=child, is_published=True).select_related('exam__course')
        submissions = AssignmentSubmission.objects.filter(student=child, is_graded=True).select_related('assignment__course')

    context = {
        'children': children,
        'child': child,
        'enrollments': enrollments,
        'exam_results': exam_results,
        'submissions': submissions,
    }
    return render(request, 'parent/grades.html', context)


@parent_required
def parent_timetable(request):
    """
    View weekly class timetable schedule for child.
    """
    children, child = _get_parent_student(request)
    schedules = []

    if child:
        enrolled_course_ids = Enrollment.objects.filter(student=child, is_active=True).values_list('course_id', flat=True)
        schedules = TimetableSchedule.objects.filter(course_id__in=enrolled_course_ids).select_related('course__instructor__user').order_by('day_of_week', 'start_time')

    context = {
        'children': children,
        'child': child,
        'schedules': schedules,
    }
    return render(request, 'parent/timetable.html', context)


@parent_required
def parent_teachers(request):
    """
    Directory of instructors teaching the child's courses.
    """
    children, child = _get_parent_student(request)
    teachers = []

    if child:
        courses = Course.objects.filter(enrollments__student=child, instructor__isnull=False).select_related('instructor__user', 'instructor__department')
        teachers = Instructor.objects.filter(courses__in=courses).distinct().select_related('user', 'department')

    context = {
        'children': children,
        'child': child,
        'teachers': teachers,
    }
    return render(request, 'parent/teachers.html', context)


@parent_required
def parent_inbox(request):
    """
    Direct messaging system for parents.
    """
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient_id')
        subject = request.POST.get('subject', '').strip()
        body = request.POST.get('body', '').strip()

        if recipient_id and subject and body:
            recipient = get_object_or_404(User, id=recipient_id)
            Message.objects.create(
                sender=request.user,
                recipient=recipient,
                subject=subject,
                body=body
            )
            messages.success(request, f'Message sent to {recipient.username}.')
            return redirect('parent_inbox')

    received_messages = Message.objects.filter(recipient=request.user).select_related('sender').order_by('-sent_at')
    sent_messages = Message.objects.filter(sender=request.user).select_related('recipient').order_by('-sent_at')
    
    # Teachers and Admins for recipient selection
    recipients = User.objects.filter(Q(is_staff=True) | Q(userprofile__role='teacher')).exclude(id=request.user.id).order_by('username')

    context = {
        'received_messages': received_messages,
        'sent_messages': sent_messages,
        'recipients': recipients,
    }
    return render(request, 'parent/inbox.html', context)


@parent_required
def parent_announcements(request):
    """
    School announcements & bulletins.
    """
    announcements = Announcement.objects.filter(is_published=True).order_by('-publish_date')
    context = {'announcements': announcements}
    return render(request, 'parent/announcements.html', context)


@parent_required
def parent_profile(request):
    """
    Parent profile management.
    """
    profile, _ = UserProfile.objects.get_or_create(user=request.user, defaults={'role': 'parent'})

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        parent_phone = request.POST.get('parent_phone', '').strip()

        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.save()

        profile.parent_phone = parent_phone
        profile.save()

        messages.success(request, 'Your parent profile was updated successfully!')
        return redirect('parent_profile')

    children = Student.objects.filter(parent=request.user)
    context = {
        'profile': profile,
        'children_count': children.count(),
    }
    return render(request, 'parent/profile.html', context)
