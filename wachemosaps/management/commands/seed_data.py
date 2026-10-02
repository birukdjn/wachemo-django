"""
Custom Django Management Command: seed_data
Populates WSaPS with official initial data:
- 5 Admin accounts (Birukdjn / Birukdjn@8325, admin1..admin4 / Admin1@123!)
- 50 Teacher accounts (teacher1 .. teacher50 / Teacher1@123! .. Teacher50@123!)
- 200 Parent accounts (parent1 .. parent200 / Parent1@123! .. Parent200@123!)
- 1000 Student accounts (student1 .. student1000 / Student1@123! .. Student1000@123!)
- Departments, Courses, Enrollments, Grades, Exams, Attendance, Library Books, Announcements, Messages, Clubs, News, Events.
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
    help = 'Seeds database with 1000 students, 50 teachers, 200 parents, 5 admins, and domain data.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting WSaPS large-scale database seeding (1000 Students, 50 Teachers, 200 Parents, 5 Admins)...'))
        
        with transaction.atomic():
            # 1. 5 Admins
            admin_data = [
                ('Birukdjn', 'birukedjn@gmail.com', 'Biruk', 'Dejene', 'Birukdjn@8325'),
                ('admin1', 'admin1@wachemo.edu.et', 'Ato Solomon', 'Admin', 'Admin1@123!'),
                ('admin2', 'admin2@wachemo.edu.et', 'W/ro Tigist', 'Admin', 'Admin2@123!'),
                ('admin3', 'admin3@wachemo.edu.et', 'Ato Dawit', 'Admin', 'Admin3@123!'),
                ('admin4', 'admin4@wachemo.edu.et', 'W/ro Meron', 'Admin', 'Admin4@123!'),
            ]
            
            main_admin = None
            for uname, uemail, ufirst, ulast, upass in admin_data:
                u, _ = User.objects.get_or_create(username=uname)
                u.email = uemail
                u.first_name = ufirst
                u.last_name = ulast
                u.is_staff = True
                u.is_superuser = True
                u.set_password(upass)
                u.save()
                UserProfile.objects.update_or_create(user=u, defaults={'role': 'admin'})
                if uname == 'Birukdjn':
                    main_admin = u
            self.stdout.write(self.style.SUCCESS('  ✓ 5 Admins created (Birukdjn, admin1..admin4)'))

            # Helper for Department
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
            self.stdout.write(self.style.SUCCESS('  ✓ 5 Departments verified'))

            # 3. 50 Teachers (teacher1..teacher50)
            instructors = []
            teacher_users = []
            for i in range(1, 51):
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

            self.stdout.write(self.style.SUCCESS('  ✓ 50 Teachers created (teacher1 .. teacher50)'))

            # 4. 200 Parents (parent1..parent200)
            parents = []
            for p in range(1, 201):
                p_username = f"parent{p}"
                p_email = f"parent{p}@gmail.com"
                p_first = FIRST_NAMES[(p + 3) % len(FIRST_NAMES)]
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
            self.stdout.write(self.style.SUCCESS('  ✓ 200 Parents created (parent1 .. parent200)'))

            # Helper for Student
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

            # 5. 1000 Students (student1..student1000)
            students = []
            for s in range(1, 1001):
                s_username = f"student{s}"
                s_email = f"student{s}@wachemo.edu.et"
                s_first = FIRST_NAMES[(s - 1) % len(FIRST_NAMES)]
                s_last = LAST_NAMES[(s + 7) % len(LAST_NAMES)]
                s_password = f"Student{s}@123!"
                stu_id = f"STU{s:04d}"
                assigned_parent = parents[(s - 1) % len(parents)]
                assigned_dept = depts[(s - 1) % len(depts)]
                calc_gpa = round(2.5 + ((s * 13) % 15) * 0.1, 2)

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

            self.stdout.write(self.style.SUCCESS('  ✓ 1000 Students created (student1 .. student1000)'))

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

            # 6. Courses (20 active courses across departments)
            all_courses = []
            for idx in range(1, 21):
                dept_obj = depts[(idx - 1) % len(depts)]
                inst_obj = instructors[(idx - 1) % len(instructors)]
                code = f"{dept_obj.code}{100 + idx}"
                c = get_or_create_course(code, f"{dept_obj.name} Module {idx}", inst_obj, dept_obj, 3 + (idx % 2))
                all_courses.append(c)
                
            self.stdout.write(self.style.SUCCESS('  ✓ 20 Courses created across departments'))

            # 7. Enrollments & Attendance for all 1000 Students
            grade_list = ['A', 'B', 'A-', 'B+', 'C+', 'A+']
            for s_idx, stu in enumerate(students):
                c1 = all_courses[(s_idx) % len(all_courses)]
                c2 = all_courses[(s_idx + 1) % len(all_courses)]
                
                g1 = grade_list[s_idx % len(grade_list)]
                g2 = grade_list[(s_idx + 3) % len(grade_list)]

                Enrollment.objects.update_or_create(
                    student=stu, course=c1,
                    defaults={'semester': 'Semester 1', 'academic_year': '2025/2026', 'grade': g1}
                )
                Enrollment.objects.update_or_create(
                    student=stu, course=c2,
                    defaults={'semester': 'Semester 1', 'academic_year': '2025/2026', 'grade': g2}
                )
                
                if s_idx < 100:
                    Attendance.objects.update_or_create(
                        student=stu, course=c1, date=date.today(),
                        defaults={'status': 'present', 'marked_by': c1.instructor, 'notes': 'Present'}
                    )

            self.stdout.write(self.style.SUCCESS('  ✓ Enrollments created for 1000 students'))

            # 8. Assignments & Submissions
            assign1, _ = Assignment.objects.update_or_create(
                course=all_courses[0], title='Python Loops & Recursion',
                defaults={'description': 'Complete all 5 Python programming challenges.', 'due_date': timezone.now() + timedelta(days=7), 'max_points': 100, 'is_published': True}
            )
            for stu in students[:50]:
                AssignmentSubmission.objects.update_or_create(
                    assignment=assign1, student=stu,
                    defaults={'submission_text': '# Python Submission\ndef factorial(n):\n    return 1 if n<=1 else n*factorial(n-1)', 'points_earned': 95, 'is_graded': True, 'feedback': 'Great job!'}
                )

            # 9. Exams & Exam Results
            exam1, _ = Exam.objects.update_or_create(
                course=all_courses[0], title='Midterm Examination',
                defaults={'exam_type': 'midterm', 'exam_date': timezone.now() + timedelta(days=14), 'duration_minutes': 120, 'max_points': 100, 'is_published': True}
            )
            for stu in students[:50]:
                ExamResult.objects.update_or_create(
                    exam=exam1, student=stu,
                    defaults={'points_earned': 85 + (stu.id % 15), 'grade': 'A', 'is_published': True, 'feedback': 'Exceeded expectations.'}
                )

            # 10. Announcements & Messages
            Announcement.objects.update_or_create(
                title='Welcome to Academic Year 2025/2026',
                defaults={'content': 'Classes for Semester 1 have officially commenced across all departments.', 'priority': 'high', 'target_audience': 'all', 'is_published': True, 'created_by': main_admin}
            )
            Message.objects.update_or_create(
                sender=teacher_users[0], recipient=students[0].user, subject='Assignment Feedback',
                defaults={'body': 'Great work on the Python recursion assignment!'}
            )

            # 11. News, Gallery, Events, Newsletter, Contact Messages
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
            
            self.stdout.write(self.style.SUCCESS('\n✓ Database Seeding Successfully Completed (5 Admins, 50 Teachers, 200 Parents, 1000 Students, 20 Courses)!'))
