"""
Custom Django Management Command: seed_data
Populates WSaPS with official initial data for Admin, Teachers, Students, Parents, Courses,
Departments, Enrollments, Grades, Exams, Attendance, Library, Announcements, Clubs, News, Gallery, Events, Subscribers, and Contact Messages.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction, models
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from wachemosaps.models import UserProfile, News, Gallery, Event, NewsletterSubscriber, ContactMessage
from student.models import (
    Department, Instructor, Student, Course, Enrollment,
    Assignment, AssignmentSubmission, Attendance, Exam, ExamResult,
    Book, BookBorrowing, Announcement, Notification, TimetableSchedule,
    Message, StudentClub, ClubMembership
)

class Command(BaseCommand):
    help = 'Seeds database with initial production and testing data.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting WSaPS database seeding...'))
        
        with transaction.atomic():
            # 1. Admin Superuser: Birukdjn / Birukdjn@8325 / birukedjn@gmail.com
            admin_user, _ = User.objects.get_or_create(username='Birukdjn')
            admin_user.email = 'birukedjn@gmail.com'
            admin_user.first_name = 'Biruk'
            admin_user.last_name = 'Dejene'
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.set_password('Birukdjn@8325')
            admin_user.save()
            UserProfile.objects.update_or_create(user=admin_user, defaults={'role': 'admin'})
            self.stdout.write(self.style.SUCCESS('  ✓ Admin User: Birukdjn (birukedjn@gmail.com)'))

            # Helper for Department safely
            def get_or_create_dept(code, name, description):
                dept = Department.objects.filter(models.Q(code=code) | models.Q(name=name)).first()
                if dept:
                    dept.code = code
                    dept.name = name
                    dept.description = description
                    dept.save()
                else:
                    dept = Department.objects.create(code=code, name=name, description=description)
                return dept

            # 2. Departments
            dept_cs = get_or_create_dept('CS', 'Computer Science', 'Software & Computing')
            dept_ns = get_or_create_dept('NS', 'Natural Sciences', 'Physics, Chemistry & Biology')
            dept_ss = get_or_create_dept('SS', 'Social Sciences', 'History, Civics & Geography')
            self.stdout.write(self.style.SUCCESS('  ✓ Departments created: CS, NS, SS'))

            # 3. Teachers / Instructors
            t1_user, _ = User.objects.get_or_create(username='teacher1')
            t1_user.email = 'teacher1@wachemo.edu.et'
            t1_user.first_name = 'Ato Solomon'
            t1_user.last_name = 'Haile'
            t1_user.set_password('Teacher1@123!')
            t1_user.save()
            UserProfile.objects.update_or_create(user=t1_user, defaults={'role': 'teacher', 'teacher_subject': 'Computer Science'})
            
            inst1 = Instructor.objects.filter(models.Q(user=t1_user) | models.Q(employee_id='EMP001')).first()
            if inst1:
                inst1.user = t1_user
                inst1.employee_id = 'EMP001'
                inst1.department = dept_cs
                inst1.phone = '+251911111111'
                inst1.specialization = 'Algorithms & Python'
                inst1.save()
            else:
                inst1 = Instructor.objects.create(
                    user=t1_user, employee_id='EMP001', department=dept_cs, phone='+251911111111', specialization='Algorithms & Python'
                )

            t2_user, _ = User.objects.get_or_create(username='teacher2')
            t2_user.email = 'teacher2@wachemo.edu.et'
            t2_user.first_name = 'W/ro Meron'
            t2_user.last_name = 'Assefa'
            t2_user.set_password('Teacher2@123!')
            t2_user.save()
            UserProfile.objects.update_or_create(user=t2_user, defaults={'role': 'teacher', 'teacher_subject': 'Physics'})
            
            inst2 = Instructor.objects.filter(models.Q(user=t2_user) | models.Q(employee_id='EMP002')).first()
            if inst2:
                inst2.user = t2_user
                inst2.employee_id = 'EMP002'
                inst2.department = dept_ns
                inst2.phone = '+251922222222'
                inst2.specialization = 'Quantum & Applied Physics'
                inst2.save()
            else:
                inst2 = Instructor.objects.create(
                    user=t2_user, employee_id='EMP002', department=dept_ns, phone='+251922222222', specialization='Quantum & Applied Physics'
                )
            self.stdout.write(self.style.SUCCESS('  ✓ Teachers created: teacher1, teacher2'))

            # 4. Parents
            p1_user, _ = User.objects.get_or_create(username='parent1')
            p1_user.email = 'parent1@gmail.com'
            p1_user.first_name = 'Ato Kebede'
            p1_user.last_name = 'Tadesse'
            p1_user.set_password('Parent1@123!')
            p1_user.save()
            UserProfile.objects.update_or_create(user=p1_user, defaults={'role': 'parent', 'parent_phone': '+251933333333'})

            p2_user, _ = User.objects.get_or_create(username='parent2')
            p2_user.email = 'parent2@gmail.com'
            p2_user.first_name = 'W/ro Genet'
            p2_user.last_name = 'Bekele'
            p2_user.set_password('Parent2@123!')
            p2_user.save()
            UserProfile.objects.update_or_create(user=p2_user, defaults={'role': 'parent', 'parent_phone': '+251944444444'})
            self.stdout.write(self.style.SUCCESS('  ✓ Parents created: parent1, parent2'))

            # Helper for Student safely
            def get_or_create_student(u_obj, s_id, parent_u, dept_obj, gpa_val):
                stu = Student.objects.filter(models.Q(user=u_obj) | models.Q(student_id=s_id)).first()
                if stu:
                    stu.user = u_obj
                    stu.student_id = s_id
                    stu.parent = parent_u
                    stu.department = dept_obj
                    stu.gpa = Decimal(str(gpa_val))
                    stu.status = 'active'
                    stu.save()
                else:
                    stu = Student.objects.create(
                        user=u_obj, student_id=s_id, parent=parent_u, department=dept_obj, gpa=Decimal(str(gpa_val)), status='active'
                    )
                return stu

            # 5. Students
            s1_user, _ = User.objects.get_or_create(username='student1')
            s1_user.email = 'student1@wachemo.edu.et'
            s1_user.first_name = 'Abebe'
            s1_user.last_name = 'Kebede'
            s1_user.set_password('Student1@123!')
            s1_user.save()
            UserProfile.objects.update_or_create(user=s1_user, defaults={'role': 'student', 'student_id': 'STU001'})
            stu1 = get_or_create_student(s1_user, 'STU001', p1_user, dept_cs, 3.85)

            s2_user, _ = User.objects.get_or_create(username='student2')
            s2_user.email = 'student2@wachemo.edu.et'
            s2_user.first_name = 'Marta'
            s2_user.last_name = 'Kebede'
            s2_user.set_password('Student2@123!')
            s2_user.save()
            UserProfile.objects.update_or_create(user=s2_user, defaults={'role': 'student', 'student_id': 'STU002'})
            stu2 = get_or_create_student(s2_user, 'STU002', p1_user, dept_ns, 3.70)

            s3_user, _ = User.objects.get_or_create(username='student3')
            s3_user.email = 'student3@wachemo.edu.et'
            s3_user.first_name = 'Dawit'
            s3_user.last_name = 'Genet'
            s3_user.set_password('Student3@123!')
            s3_user.save()
            UserProfile.objects.update_or_create(user=s3_user, defaults={'role': 'student', 'student_id': 'STU003'})
            stu3 = get_or_create_student(s3_user, 'STU003', p2_user, dept_ss, 3.90)
            self.stdout.write(self.style.SUCCESS('  ✓ Students created: student1, student2, student3'))

            # Helper for Course
            def get_or_create_course(code, name, inst, dept, credits):
                c = Course.objects.filter(code=code).first()
                if c:
                    c.name = name
                    c.instructor = inst
                    c.department = dept
                    c.credits = credits
                    c.semester = 'Semester 1'
                    c.academic_year = '2025/2026'
                    c.save()
                else:
                    c = Course.objects.create(
                        code=code, name=name, instructor=inst, department=dept, credits=credits,
                        semester='Semester 1', academic_year='2025/2026'
                    )
                return c

            # 6. Courses
            c1 = get_or_create_course('CS101', 'Introduction to Computer Science', inst1, dept_cs, 4)
            c2 = get_or_create_course('NS102', 'General Physics & STEM Laboratory', inst2, dept_ns, 4)
            c3 = get_or_create_course('SS103', 'Civics, Ethics & Global Citizenship', inst1, dept_ss, 3)
            self.stdout.write(self.style.SUCCESS('  ✓ Courses created: CS101, NS102, SS103'))

            # 7. Enrollments
            Enrollment.objects.update_or_create(student=stu1, course=c1, defaults={'semester': 'Semester 1', 'academic_year': '2025/2026', 'grade': 'A'})
            Enrollment.objects.update_or_create(student=stu2, course=c2, defaults={'semester': 'Semester 1', 'academic_year': '2025/2026', 'grade': 'B'})
            Enrollment.objects.update_or_create(student=stu3, course=c3, defaults={'semester': 'Semester 1', 'academic_year': '2025/2026', 'grade': 'A'})
            self.stdout.write(self.style.SUCCESS('  ✓ Enrollments created'))

            # 8. Assignments & Submissions
            assign1, _ = Assignment.objects.update_or_create(
                course=c1, title='Python Loops & Recursion',
                defaults={'description': 'Complete all 5 Python programming challenges.', 'due_date': timezone.now() + timedelta(days=7), 'max_points': 100, 'is_published': True}
            )
            AssignmentSubmission.objects.update_or_create(
                assignment=assign1, student=stu1,
                defaults={'submission_text': 'def factorial(n):\n    return 1 if n<=1 else n*factorial(n-1)', 'points_earned': 95, 'is_graded': True, 'feedback': 'Excellent implementation!'}
            )

            # 9. Exams & Exam Results
            exam1, _ = Exam.objects.update_or_create(
                course=c1, title='Midterm Examination',
                defaults={'exam_type': 'midterm', 'exam_date': timezone.now() + timedelta(days=14), 'duration_minutes': 120, 'max_points': 100, 'is_published': True}
            )
            ExamResult.objects.update_or_create(
                exam=exam1, student=stu1,
                defaults={'points_earned': 94, 'grade': 'A', 'is_published': True, 'feedback': 'Outstanding score.'}
            )

            # 10. Attendance
            Attendance.objects.update_or_create(student=stu1, course=c1, date=date.today(), defaults={'status': 'present', 'marked_by': inst1, 'notes': 'On time.'})
            Attendance.objects.update_or_create(student=stu2, course=c2, date=date.today(), defaults={'status': 'present', 'marked_by': inst2, 'notes': 'Active participation.'})

            # 11. Timetable Schedules
            TimetableSchedule.objects.update_or_create(
                course=c1, day_of_week='Monday', start_time='08:00:00', end_time='10:00:00',
                defaults={'room': 'Lab 101'}
            )
            TimetableSchedule.objects.update_or_create(
                course=c2, day_of_week='Tuesday', start_time='10:00:00', end_time='12:00:00',
                defaults={'room': 'Physics Lab 2'}
            )

            # 12. Announcements & Messages
            Announcement.objects.update_or_create(
                title='Welcome to Academic Year 2025/2026',
                defaults={'content': 'Classes for Semester 1 have officially commenced across all departments.', 'priority': 'high', 'target_audience': 'all', 'is_published': True, 'created_by': admin_user}
            )
            Message.objects.update_or_create(
                sender=t1_user, recipient=s1_user, subject='Assignment Feedback',
                defaults={'body': 'Great work on the Python recursion assignment!'}
            )

            # 13. Library Books & Borrowings
            book1 = Book.objects.filter(isbn='978-0134685991').first()
            if book1:
                book1.title = 'Effective Java & Python Programming'
                book1.author = 'Joshua Bloch'
                book1.category = 'textbook'
                book1.total_copies = 5
                book1.available_copies = 4
                book1.save()
            else:
                book1 = Book.objects.create(
                    isbn='978-0134685991', title='Effective Java & Python Programming', author='Joshua Bloch', category='textbook', total_copies=5, available_copies=4
                )
            
            BookBorrowing.objects.update_or_create(
                book=book1, student=stu1,
                defaults={'due_date': timezone.now() + timedelta(days=14), 'status': 'borrowed'}
            )

            # 14. Student Clubs & Memberships
            club1, _ = StudentClub.objects.update_or_create(
                name='STEM & Robotics Club',
                defaults={'description': 'Hands-on coding, microcontrollers, and robotics competitions.', 'category': 'Academic', 'advisor': inst1}
            )
            ClubMembership.objects.update_or_create(club=club1, student=stu1, defaults={'role': 'President'})

            # 15. News, Gallery, Events, Newsletter, Contact Messages
            News.objects.update_or_create(
                title='WSaPS Wins Regional STEM Championship',
                defaults={'content': 'Students from Wachemo Secondary and Preparatory School achieved 1st place in the national science fair.', 'reporter': 'Biruk Dejene', 'day': 15, 'month': 'Oct'}
            )
            Event.objects.update_or_create(
                title='Annual Science & Technology Fair 2026',
                defaults={'description': 'Showcase of student innovative projects and robotics demonstrations.', 'day': 20, 'month': 'Nov', 'location': 'Main Auditorium', 'duration': 'Full Day'}
            )
            NewsletterSubscriber.objects.update_or_create(
                email='birukedjn@gmail.com', defaults={'is_active': True}
            )
            ContactMessage.objects.update_or_create(
                email='birukedjn@gmail.com', subject='Inquiry about Admission 2026/2027',
                defaults={'name': 'Biruk Dejene', 'message': 'Hello, I would like to inquire about the upcoming admission requirements.', 'is_read': False}
            )
            
            self.stdout.write(self.style.SUCCESS('\n✓ Database Seeding Successfully Completed!'))
