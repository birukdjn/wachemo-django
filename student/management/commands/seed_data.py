import os
import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from wachemosaps.models import News, Gallery, Event, UserProfile
from student.models import (
    Department, Instructor, Student, Course, Enrollment, Assignment,
    AssignmentSubmission, Attendance, Exam, ExamResult, Book, BookBorrowing,
    Announcement, Notification, TimetableSchedule, Message, StudentClub, ClubMembership
)

class Command(BaseCommand):
    help = 'Seeds complete sample data for Wachemo Secondary & Preparatory School'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))

        # 1. Ensure Superuser Admin accounts
        admin_user, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@wsaps.edu'})
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.first_name = 'School'
        admin_user.last_name = 'Administrator'
        admin_user.set_password('Admin2026!')
        admin_user.save()
        UserProfile.objects.get_or_create(user=admin_user, defaults={'role': 'teacher', 'teacher_subject': 'Administration'})

        b_admin, _ = User.objects.get_or_create(username='Birukdjn', defaults={'email': 'Birukedjn@gmail.com'})
        b_admin.is_staff = True
        b_admin.is_superuser = True
        b_admin.first_name = 'Biruk'
        b_admin.last_name = 'Dejene'
        b_admin.set_password('Birukdjn@8325!')
        b_admin.save()
        UserProfile.objects.get_or_create(user=b_admin, defaults={'role': 'teacher', 'teacher_subject': 'Super Admin'})

        self.stdout.write(self.style.SUCCESS('Admin superusers ready (admin: Admin2026! | Birukdjn: Birukdjn@8325!)'))

        # 2. Create Departments
        depts_data = [
            {'code': 'NSC', 'name': 'Natural Sciences', 'description': 'Physics, Chemistry, Biology, and Environmental Science.'},
            {'code': 'CS', 'name': 'Computational Sciences', 'description': 'Mathematics, Computer Science, and Information Technology.'},
            {'code': 'SSC', 'name': 'Social Sciences', 'description': 'History, Geography, Civics, and Economics.'},
            {'code': 'LANG', 'name': 'Languages & Literature', 'description': 'Amharic, English, and Oromiffa Languages.'},
            {'code': 'BUS', 'name': 'Business & Commerce', 'description': 'Accounting, Entrepreneurship, and Business Management.'},
        ]
        
        dept_objs = {}
        for d in depts_data:
            dept, _ = Department.objects.get_or_create(code=d['code'], defaults={'name': d['name'], 'description': d['description']})
            dept_objs[d['code']] = dept
        self.stdout.write(self.style.SUCCESS(f'Departments created/updated: {len(dept_objs)}'))

        # 3. Create Instructors
        instructors_data = [
            {'username': 'dr_abera', 'first_name': 'Abera', 'last_name': 'Worku', 'email': 'abera.w@wsaps.edu', 'emp_id': 'EMP001', 'dept': 'NSC', 'spec': 'Physics & Thermodynamics', 'qual': 'Ph.D. in Physics', 'room': 'Lab 101'},
            {'username': 'prof_tigist', 'first_name': 'Tigist', 'last_name': 'Haile', 'email': 'tigist.h@wsaps.edu', 'emp_id': 'EMP002', 'dept': 'CS', 'spec': 'Calculus & Applied Math', 'qual': 'M.Sc. in Applied Mathematics', 'room': 'Room 204'},
            {'username': 'mr_solomon', 'first_name': 'Solomon', 'last_name': 'Tadesse', 'email': 'solomon.t@wsaps.edu', 'emp_id': 'EMP003', 'dept': 'NSC', 'spec': 'Organic Chemistry', 'qual': 'M.Sc. in Chemistry', 'room': 'Chemistry Lab 2'},
            {'username': 'mrs_bethlehem', 'first_name': 'Bethlehem', 'last_name': 'Girma', 'email': 'bethlehem.g@wsaps.edu', 'emp_id': 'EMP004', 'dept': 'NSC', 'spec': 'Molecular Biology', 'qual': 'M.Sc. in Biology', 'room': 'Biology Lab 1'},
            {'username': 'mr_dawit', 'first_name': 'Dawit', 'last_name': 'Kebede', 'email': 'dawit.k@wsaps.edu', 'emp_id': 'EMP005', 'dept': 'LANG', 'spec': 'Advanced English Grammar & Literature', 'qual': 'M.A. in English Literature', 'room': 'Humanities 3'},
        ]

        inst_objs = []
        for i_data in instructors_data:
            u, _ = User.objects.get_or_create(username=i_data['username'], defaults={'email': i_data['email'], 'first_name': i_data['first_name'], 'last_name': i_data['last_name']})
            u.set_password('Teacher2026!')
            u.is_staff = True
            u.save()
            
            UserProfile.objects.get_or_create(user=u, defaults={'role': 'teacher', 'teacher_subject': i_data['spec']})
            
            inst, _ = Instructor.objects.get_or_create(
                user=u,
                defaults={
                    'employee_id': i_data['emp_id'],
                    'department': dept_objs[i_data['dept']],
                    'specialization': i_data['spec'],
                    'qualification': i_data['qual'],
                    'office_location': i_data['room'],
                    'phone': '+251-911-234567',
                    'hire_date': date(2021, 9, 1)
                }
            )
            inst_objs.append(inst)
        self.stdout.write(self.style.SUCCESS(f'Instructors created: {len(inst_objs)}'))

        # 4. Create Students
        students_data = [
            {'username': 'biruk_djn', 'first_name': 'Biruk', 'last_name': 'Dejene', 'email': 'biruk@wsaps.edu', 'stu_id': 'STU2026001', 'dept': 'CS', 'gpa': 3.92, 'credits': 45},
            {'username': 'helen_alem', 'first_name': 'Helen', 'last_name': 'Alemu', 'email': 'helen@wsaps.edu', 'stu_id': 'STU2026002', 'dept': 'NSC', 'gpa': 3.85, 'credits': 42},
            {'username': 'yared_b', 'first_name': 'Yared', 'last_name': 'Bekele', 'email': 'yared@wsaps.edu', 'stu_id': 'STU2026003', 'dept': 'SSC', 'gpa': 3.65, 'credits': 38},
            {'username': 'selam_m', 'first_name': 'Selam', 'last_name': 'Mekonnen', 'email': 'selam@wsaps.edu', 'stu_id': 'STU2026004', 'dept': 'LANG', 'gpa': 3.78, 'credits': 40},
            {'username': 'samuel_k', 'first_name': 'Samuel', 'last_name': 'Kassahun', 'email': 'samuel@wsaps.edu', 'stu_id': 'STU2026005', 'dept': 'BUS', 'gpa': 3.50, 'credits': 36},
        ]

        stu_objs = []
        for s_data in students_data:
            u, _ = User.objects.get_or_create(username=s_data['username'], defaults={'email': s_data['email'], 'first_name': s_data['first_name'], 'last_name': s_data['last_name']})
            u.set_password('Student2026!')
            u.save()

            UserProfile.objects.get_or_create(user=u, defaults={'role': 'student', 'student_id': s_data['stu_id']})

            stu, _ = Student.objects.get_or_create(
                user=u,
                defaults={
                    'student_id': s_data['stu_id'],
                    'department': dept_objs[s_data['dept']],
                    'phone': '+251-912-345678',
                    'address': 'Hossana, Ethiopia',
                    'date_of_birth': date(2007, 5, 14),
                    'enrollment_date': date(2024, 9, 15),
                    'status': 'active',
                    'gpa': s_data['gpa'],
                    'credits_completed': s_data['credits'],
                    'credits_required': 120,
                    'emergency_contact': 'Parent Contact',
                    'emergency_phone': '+251-911-000111'
                }
            )
            stu_objs.append(stu)
        self.stdout.write(self.style.SUCCESS(f'Students created: {len(stu_objs)}'))

        # 5. Create Courses
        courses_data = [
            {'code': 'PHYS101', 'name': 'Introductory Physics', 'dept': 'NSC', 'inst': inst_objs[0], 'credits': 4, 'desc': 'Fundamentals of mechanics, thermodynamics, and wave optics.'},
            {'code': 'MATH201', 'name': 'Advanced Mathematics & Calculus', 'dept': 'CS', 'inst': inst_objs[1], 'credits': 4, 'desc': 'Calculus, linear algebra, differential equations, and vectors.'},
            {'code': 'CHEM102', 'name': 'General & Organic Chemistry', 'dept': 'NSC', 'inst': inst_objs[2], 'credits': 3, 'desc': 'Atomic structures, chemical bonding, and organic synthesis.'},
            {'code': 'BIOL103', 'name': 'General Biology & Genetics', 'dept': 'NSC', 'inst': inst_objs[3], 'credits': 3, 'desc': 'Cellular biology, genetics, ecosystems, and human physiology.'},
            {'code': 'ENG202', 'name': 'Advanced English & Rhetoric', 'dept': 'LANG', 'inst': inst_objs[4], 'credits': 3, 'desc': 'Academic essay writing, public speaking, and world literature.'},
        ]

        course_objs = []
        for c_data in courses_data:
            c, _ = Course.objects.get_or_create(
                code=c_data['code'],
                defaults={
                    'name': c_data['name'],
                    'department': dept_objs[c_data['dept']],
                    'instructor': c_data['inst'],
                    'credits': c_data['credits'],
                    'description': c_data['desc'],
                    'semester': 'Semester I',
                    'academic_year': '2026',
                    'is_active': True,
                    'is_featured': True
                }
            )
            course_objs.append(c)
        self.stdout.write(self.style.SUCCESS(f'Courses created: {len(course_objs)}'))

        # 6. Enrollments
        for stu in stu_objs:
            for course in course_objs[:3]:
                Enrollment.objects.get_or_create(
                    student=stu,
                    course=course,
                    semester='Semester I',
                    academic_year='2026',
                    defaults={'grade': 'A', 'is_active': True}
                )

        # 7. Assignments & Submissions
        for course in course_objs:
            assign, _ = Assignment.objects.get_or_create(
                course=course,
                title=f'{course.name} - Assignment 1',
                defaults={
                    'description': f'Comprehensive problem set and research analysis for {course.name}.',
                    'due_date': timezone.now() + timedelta(days=10),
                    'max_points': 100,
                    'is_published': True
                }
            )
            for stu in stu_objs[:3]:
                AssignmentSubmission.objects.get_or_create(
                    assignment=assign,
                    student=stu,
                    defaults={
                        'submission_text': f'Submitted solutions for {assign.title} by {stu.get_full_name()}.',
                        'points_earned': 95,
                        'feedback': 'Excellent work, clear step-by-step logic.',
                        'is_graded': True
                    }
                )

        # 8. Exams & Exam Results
        for course in course_objs:
            ex, _ = Exam.objects.get_or_create(
                course=course,
                title=f'{course.name} Midterm Examination',
                defaults={
                    'exam_type': 'midterm',
                    'description': 'Main midterm evaluation covering chapters 1 to 4.',
                    'exam_date': timezone.now() + timedelta(days=20),
                    'duration_minutes': 120,
                    'max_points': 100,
                    'location': 'Hall A',
                    'is_published': True
                }
            )
            for stu in stu_objs[:3]:
                ExamResult.objects.get_or_create(
                    exam=ex,
                    student=stu,
                    defaults={
                        'points_earned': 92,
                        'grade': 'A',
                        'feedback': 'Great performance across all exam sections.',
                        'is_published': True
                    }
                )

        # 9. Books & Borrowing
        books_data = [
            {'title': 'University Physics with Modern Physics', 'author': 'Sears and Zemansky', 'isbn': '978-0135159552', 'category': 'textbook', 'copies': 15, 'year': 2022},
            {'title': 'Calculus: Early Transcendentals', 'author': 'James Stewart', 'isbn': '978-1337613927', 'category': 'textbook', 'copies': 20, 'year': 2021},
            {'title': 'Organic Chemistry Principles', 'author': 'Paula Yurkanis Bruice', 'isbn': '978-0134042282', 'category': 'reference', 'copies': 10, 'year': 2020},
            {'title': 'Campbell Biology 12th Edition', 'author': 'Lisa A. Urry', 'isbn': '978-0135188743', 'category': 'textbook', 'copies': 12, 'year': 2023},
        ]
        for b in books_data:
            book, _ = Book.objects.get_or_create(
                title=b['title'],
                defaults={
                    'author': b['author'],
                    'isbn': b['isbn'],
                    'category': b['category'],
                    'total_copies': b['copies'],
                    'available_copies': b['copies'] - 1,
                    'publication_year': b['year'],
                    'location': 'Shelf B-4'
                }
            )
            BookBorrowing.objects.get_or_create(
                book=book,
                student=stu_objs[0],
                defaults={'due_date': timezone.now() + timedelta(days=14), 'status': 'borrowed'}
            )

        # 10. Announcements
        announcements_data = [
            {'title': 'Annual Science & Innovation Fair 2026', 'content': 'All students are invited to submit their STEM project proposals before October 25th.', 'priority': 'high'},
            {'title': 'Semester I Midterm Examination Schedule', 'content': 'The official midterm exam timetable has been posted on the student dashboard.', 'priority': 'urgent'},
            {'title': 'New Digital Library Access Available', 'content': 'Students can now access over 10,000 online journals and e-books using their student credentials.', 'priority': 'medium'},
        ]
        for a in announcements_data:
            Announcement.objects.get_or_create(
                title=a['title'],
                defaults={
                    'content': a['content'],
                    'priority': a['priority'],
                    'target_audience': 'all',
                    'is_published': True,
                    'created_by': admin_user
                }
            )

        # 11. Student Clubs
        clubs_data = [
            {'name': 'Wachemo STEM & Robotics Club', 'cat': 'Technology', 'desc': 'Building innovative robotics and electronics projects.', 'icon': 'fa-robot'},
            {'name': 'Debate & Public Speaking Society', 'cat': 'Humanities', 'desc': 'Enhancing critical thinking and public advocacy.', 'icon': 'fa-comments'},
            {'name': 'Green Environment & Ecology Club', 'cat': 'Science', 'desc': 'Promoting sustainability and campus greening.', 'icon': 'fa-leaf'},
        ]
        for cl in clubs_data:
            club, _ = StudentClub.objects.get_or_create(
                name=cl['name'],
                defaults={
                    'category': cl['cat'],
                    'description': cl['desc'],
                    'logo_icon': cl['icon'],
                    'advisor': inst_objs[0]
                }
            )
            ClubMembership.objects.get_or_create(
                club=club,
                student=stu_objs[0],
                defaults={'role': 'President'}
            )

        # 12. News & Events for Homepage
        News.objects.get_or_create(
            title='Wachemo Secondary Achieves Top Regional Academic Honors',
            defaults={
                'content': 'Wachemo Secondary & Preparatory School students secured top percentile rankings in the national academic assessments.',
                'reporter': 'Academic Affairs Office',
                'day': 15,
                'month': 'Oct',
                'image': 'https://images.unsplash.com/photo-1523240795612-9a054b0db644?q=80&w=1200&auto=format&fit=crop'
            }
        )
        
        Event.objects.get_or_create(
            title='Parent-Teacher Conference & Progress Review',
            defaults={
                'description': 'Bi-annual meeting for parents and teachers to discuss student academic growth and achievements.',
                'day': 22,
                'month': 'Oct',
                'location': 'Main Auditorium',
                'duration': '9:00 AM - 3:00 PM'
            }
        )

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
