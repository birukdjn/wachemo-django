"""
Custom Django Management Command: seed_data
Populates WSaPS with official initial data for Admin, 20 Teachers, 100 Students, 25 Parents, Courses,
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

FIRST_NAMES = [
    "Abebe", "Marta", "Dawit", "Bethlehem", "Ephrem", "Tigist", "Yared", "Hiwot", "Kaleb", "Selam",
    "Solomon", "Meron", "Kebede", "Genet", "Tadesse", "Bekele", "Henok", "Rahel", "Daniel", "Eden",
    "Samuel", "Helen", "Mikias", "Mahlet", "Biniam", "Tsion", "Abel", "Ruth", "Elias", "Saba",
    "Robel", "Mekdes", "Fitsum", "Frehiwot", "Natan", "Aynalem", "Yonatan", "Liya", "Dagmawi", "Messay"
]

LAST_NAMES = [
    "Kebede", "Tadesse", "Bekele", "Genet", "Assefa", "Haile", "Dejene", "Worku", "Tilahun", "Mengistu",
    "Girma", "Alemu", "Tessema", "Befekadu", "Kassa", "Wolde", "Berhanu", "Abebe", "Desta", "Tekle"
]

SUBJECTS = {
    'CS': ('Computer Science', 'Algorithms & Python'),
    'NS': ('Physics', 'Quantum & Applied Physics'),
    'SS': ('Social Sciences', 'Civics & History'),
    'MATH': ('Mathematics', 'Calculus & Statistics'),
    'LANG': ('Languages', 'English & Amharic Literature')
}

class Command(BaseCommand):
    help = 'Seeds database with 100 students, 20 teachers, 25 parents, and complete domain data.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting WSaPS database seeding (100 Students, 20 Teachers)...'))
        
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
            dept_math = get_or_create_dept('MATH', 'Mathematics', 'Pure & Applied Mathematics')
            dept_lang = get_or_create_dept('LANG', 'Languages', 'English, Amharic & Literature')
            depts = [dept_cs, dept_ns, dept_ss, dept_math, dept_lang]
            self.stdout.write(self.style.SUCCESS('  ✓ Departments created: CS, NS, SS, MATH, LANG'))

            # 3. 20 Teachers / Instructors (teacher1..teacher20)
            instructors = []
            teacher_users = []
            for i in range(1, 21):
                t_username = f"teacher{i}"
                t_email = f"teacher{i}@wachemo.edu.et"
                t_first = FIRST_NAMES[(i - 1) % len(FIRST_NAMES)]
                t_last = LAST_NAMES[(i - 1) % len(LAST_NAMES)]
                t_password = f"Teacher{i}@123!"
                emp_id = f"EMP{i:03d}"

                t_user, _ = User.objects.get_or_create(username=t_username)
                t_user.email = t_email
                t_user.first_name = t_first
                t_user.last_name = t_last
                t_user.set_password(t_password)
                t_user.save()
                
                target_dept = depts[(i - 1) % len(depts)]
                subj_name, spec_name = SUBJECTS[target_dept.code]
                
                UserProfile.objects.update_or_create(
                    user=t_user, defaults={'role': 'teacher', 'teacher_subject': subj_name}
                )
                
                inst = Instructor.objects.filter(models.Q(user=t_user) | models.Q(employee_id=emp_id)).first()
                if inst:
                    inst.user = t_user
                    inst.employee_id = emp_id
                    inst.department = target_dept
                    inst.phone = f"+251911{i:06d}"
                    inst.specialization = spec_name
                    inst.save()
                else:
                    inst = Instructor.objects.create(
                        user=t_user, employee_id=emp_id, department=target_dept, phone=f"+251911{i:06d}", specialization=spec_name
                    )
                instructors.append(inst)
                teacher_users.append(t_user)

            self.stdout.write(self.style.SUCCESS('  ✓ 20 Teachers created (teacher1 .. teacher20)'))

            # 4. 25 Parents (parent1..parent25)
            parents = []
            for p in range(1, 26):
                p_username = f"parent{p}"
                p_email = f"parent{p}@gmail.com"
                p_first = FIRST_NAMES[(p + 5) % len(FIRST_NAMES)]
                p_last = LAST_NAMES[p % len(LAST_NAMES)]
                p_password = f"Parent{p}@123!"
                
                p_user, _ = User.objects.get_or_create(username=p_username)
                p_user.email = p_email
                p_user.first_name = p_first
                p_user.last_name = p_last
                p_user.set_password(p_password)
                p_user.save()
                
                UserProfile.objects.update_or_create(
                    user=p_user, defaults={'role': 'parent', 'parent_phone': f"+251933{p:06d}"}
                )
                parents.append(p_user)
            self.stdout.write(self.style.SUCCESS('  ✓ 25 Parents created (parent1 .. parent25)'))

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

            # 5. 100 Students (student1..student100)
            students = []
            for s in range(1, 101):
                s_username = f"student{s}"
                s_email = f"student{s}@wachemo.edu.et"
                s_first = FIRST_NAMES[(s - 1) % len(FIRST_NAMES)]
                s_last = LAST_NAMES[(s + 3) % len(LAST_NAMES)]
                s_password = f"Student{s}@123!"
                stu_id = f"STU{s:03d}"
                assigned_parent = parents[(s - 1) // 4]
                assigned_dept = depts[(s - 1) % len(depts)]
                calc_gpa = round(3.0 + ((s * 7) % 10) * 0.1, 2)

                s_user, _ = User.objects.get_or_create(username=s_username)
                s_user.email = s_email
                s_user.first_name = s_first
                s_user.last_name = s_last
                s_user.set_password(s_password)
                s_user.save()
                
                UserProfile.objects.update_or_create(
                    user=s_user, defaults={'role': 'student', 'student_id': stu_id}
                )
                stu_obj = get_or_create_student(s_user, stu_id, assigned_parent, assigned_dept, calc_gpa)
                students.append(stu_obj)

            self.stdout.write(self.style.SUCCESS('  ✓ 100 Students created (student1 .. student100)'))

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
            c_cs1 = get_or_create_course('CS101', 'Introduction to Computer Science', instructors[0], dept_cs, 4)
            c_cs2 = get_or_create_course('CS201', 'Data Structures & Algorithms', instructors[5], dept_cs, 4)
            c_ns1 = get_or_create_course('NS102', 'General Physics & STEM Lab', instructors[1], dept_ns, 4)
            c_ns2 = get_or_create_course('NS202', 'Organic Chemistry & Biology', instructors[6], dept_ns, 4)
            c_ss1 = get_or_create_course('SS103', 'Civics, Ethics & Citizenship', instructors[2], dept_ss, 3)
            c_ss2 = get_or_create_course('SS203', 'World History & Geography', instructors[7], dept_ss, 3)
            c_m1 = get_or_create_course('MATH101', 'Calculus & Analytical Geometry', instructors[3], dept_math, 4)
            c_m2 = get_or_create_course('MATH201', 'Probability & Statistics', instructors[8], dept_math, 3)
            c_l1 = get_or_create_course('LANG101', 'English Communication & Literature', instructors[4], dept_lang, 3)
            c_l2 = get_or_create_course('LANG201', 'Amharic Grammar & Composition', instructors[9], dept_lang, 3)
            
            all_courses = [c_cs1, c_cs2, c_ns1, c_ns2, c_ss1, c_ss2, c_m1, c_m2, c_l1, c_l2]
            self.stdout.write(self.style.SUCCESS('  ✓ 10 Courses created across departments'))

            # 7. Enrollments & Attendance & Grades for all 100 Students
            grade_list = ['A', 'B', 'A-', 'B+', 'C+']
            for s_idx, stu in enumerate(students):
                # Each student enrolled in 2 courses matching their dept + general course
                primary_course = all_courses[(s_idx * 2) % len(all_courses)]
                secondary_course = all_courses[(s_idx * 2 + 1) % len(all_courses)]
                
                g1 = grade_list[s_idx % len(grade_list)]
                g2 = grade_list[(s_idx + 2) % len(grade_list)]

                Enrollment.objects.update_or_create(
                    student=stu, course=primary_course,
                    defaults={'semester': 'Semester 1', 'academic_year': '2025/2026', 'grade': g1}
                )
                Enrollment.objects.update_or_create(
                    student=stu, course=secondary_course,
                    defaults={'semester': 'Semester 1', 'academic_year': '2025/2026', 'grade': g2}
                )
                
                # Attendance
                Attendance.objects.update_or_create(
                    student=stu, course=primary_course, date=date.today(),
                    defaults={'status': 'present', 'marked_by': primary_course.instructor, 'notes': 'Attended lecture'}
                )

            self.stdout.write(self.style.SUCCESS('  ✓ Enrollments & Attendance created for 100 students'))

            # 8. Assignments & Submissions
            assign1, _ = Assignment.objects.update_or_create(
                course=c_cs1, title='Python Loops & Recursion',
                defaults={'description': 'Complete all 5 Python programming challenges.', 'due_date': timezone.now() + timedelta(days=7), 'max_points': 100, 'is_published': True}
            )
            for stu in students[:15]:
                AssignmentSubmission.objects.update_or_create(
                    assignment=assign1, student=stu,
                    defaults={'submission_text': '# Python Code Submission\ndef factorial(n):\n    return 1 if n<=1 else n*factorial(n-1)', 'points_earned': 95, 'is_graded': True, 'feedback': 'Excellent work!'}
                )

            # 9. Exams & Exam Results
            exam1, _ = Exam.objects.update_or_create(
                course=c_cs1, title='Midterm Examination',
                defaults={'exam_type': 'midterm', 'exam_date': timezone.now() + timedelta(days=14), 'duration_minutes': 120, 'max_points': 100, 'is_published': True}
            )
            for stu in students[:20]:
                ExamResult.objects.update_or_create(
                    exam=exam1, student=stu,
                    defaults={'points_earned': 88 + (stu.id % 12), 'grade': 'A', 'is_published': True, 'feedback': 'Strong analytical performance.'}
                )

            # 10. Timetable Schedules
            for idx, crs in enumerate(all_courses):
                days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
                TimetableSchedule.objects.update_or_create(
                    course=crs, day_of_week=days[idx % 5], start_time=f"{8 + (idx % 4)*2:02d}:00:00", end_time=f"{10 + (idx % 4)*2:02d}:00:00",
                    defaults={'room': f"Room {101 + idx}"}
                )

            # 11. Announcements & Messages
            Announcement.objects.update_or_create(
                title='Welcome to Academic Year 2025/2026',
                defaults={'content': 'Classes for Semester 1 have officially commenced across all departments.', 'priority': 'high', 'target_audience': 'all', 'is_published': True, 'created_by': admin_user}
            )
            Message.objects.update_or_create(
                sender=teacher_users[0], recipient=students[0].user, subject='Assignment Feedback',
                defaults={'body': 'Great work on the Python recursion assignment!'}
            )

            # 12. Library Books & Borrowings
            book1 = Book.objects.filter(isbn='978-0134685991').first()
            if book1:
                book1.title = 'Effective Java & Python Programming'
                book1.author = 'Joshua Bloch'
                book1.category = 'textbook'
                book1.total_copies = 20
                book1.available_copies = 15
                book1.save()
            else:
                book1 = Book.objects.create(
                    isbn='978-0134685991', title='Effective Java & Python Programming', author='Joshua Bloch', category='textbook', total_copies=20, available_copies=15
                )
            
            for stu in students[:5]:
                BookBorrowing.objects.update_or_create(
                    book=book1, student=stu,
                    defaults={'due_date': timezone.now() + timedelta(days=14), 'status': 'borrowed'}
                )

            # 13. Student Clubs & Memberships
            club1, _ = StudentClub.objects.update_or_create(
                name='STEM & Robotics Club',
                defaults={'description': 'Hands-on coding, microcontrollers, and robotics competitions.', 'category': 'Academic', 'advisor': instructors[0]}
            )
            for idx, stu in enumerate(students[:10]):
                ClubMembership.objects.update_or_create(club=club1, student=stu, defaults={'role': 'President' if idx == 0 else 'Member'})

            # 14. News, Gallery, Events, Newsletter, Contact Messages
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
            
            self.stdout.write(self.style.SUCCESS('\n✓ Database Seeding Successfully Completed (Admin, 100 Students, 20 Teachers, 25 Parents, 10 Courses)!'))
