from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from wachemosaps.models import UserProfile
from student.models import Department, Instructor, Student, Course, Enrollment, Assignment, AssignmentSubmission, Exam, ExamResult, Message, Notification

class RBACAndSecurityTestCase(TestCase):
    def setUp(self):
        # 1. Setup Users & Roles
        self.admin_user = User.objects.create_superuser(username='admin_test', password='password123', email='admin@test.com')
        UserProfile.objects.create(user=self.admin_user, role='admin')

        self.teacher1_user = User.objects.create_user(username='teacher1', password='password123', email='t1@test.com')
        UserProfile.objects.create(user=self.teacher1_user, role='teacher')
        self.dept = Department.objects.create(name='Computer Science', code='CS')
        self.instructor1 = Instructor.objects.create(user=self.teacher1_user, employee_id='EMP001', department=self.dept)

        self.teacher2_user = User.objects.create_user(username='teacher2', password='password123', email='t2@test.com')
        UserProfile.objects.create(user=self.teacher2_user, role='teacher')
        self.instructor2 = Instructor.objects.create(user=self.teacher2_user, employee_id='EMP002', department=self.dept)

        self.student1_user = User.objects.create_user(username='student1', password='password123', email='s1@test.com')
        UserProfile.objects.create(user=self.student1_user, role='student')
        self.student1 = Student.objects.create(user=self.student1_user, student_id='STU001', department=self.dept)

        self.student2_user = User.objects.create_user(username='student2', password='password123', email='s2@test.com')
        UserProfile.objects.create(user=self.student2_user, role='student')
        self.student2 = Student.objects.create(user=self.student2_user, student_id='STU002', department=self.dept)

        self.parent1_user = User.objects.create_user(username='parent1', password='password123', email='p1@test.com')
        UserProfile.objects.create(user=self.parent1_user, role='parent')
        self.student1.parent = self.parent1_user
        self.student1.save()

        # 2. Setup Course & Enrollment
        self.course1 = Course.objects.create(code='CS101', name='Intro to Programming', instructor=self.instructor1, department=self.dept)
        self.enrollment1 = Enrollment.objects.create(student=self.student1, course=self.course1, semester='Fall 2026', academic_year='2025/2026')

        self.client = Client()

    def test_admin_cannot_edit_student_grade(self):
        """Verify Admin receives rejection error when attempting to edit student grade directly."""
        self.client.login(username='admin_test', password='password123')
        response = self.client.post(reverse('admin_enrollments'), {
            'action': 'update_grade',
            'enrollment_id': self.enrollment1.id,
            'grade': 'A'
        }, follow=True)
        
        self.enrollment1.refresh_from_db()
        self.assertNotEqual(self.enrollment1.grade, 'A')
        self.assertContains(response, "Security Policy Violation")

    def test_teacher_can_grade_assigned_course_only(self):
        """Verify Teacher 1 can grade assigned course CS101, but Teacher 2 cannot grade CS101."""
        # Teacher 1 grading CS101
        self.client.login(username='teacher1', password='password123')
        assignment = Assignment.objects.create(course=self.course1, title='HW1', description='Test', due_date='2026-12-31 23:59:00', max_points=100)
        submission = AssignmentSubmission.objects.create(assignment=assignment, student=self.student1, submission_text='Code')
        
        res = self.client.post(reverse('teacher_grade_submission', args=[submission.id]), {
            'points_earned': 95,
            'feedback': 'Great job'
        })
        submission.refresh_from_db()
        self.assertEqual(submission.points_earned, 95)

        # Teacher 2 attempting to grade CS101 submission
        self.client.logout()
        self.client.login(username='teacher2', password='password123')
        res2 = self.client.post(reverse('teacher_grade_submission', args=[submission.id]), {
            'points_earned': 50,
            'feedback': 'Hacked'
        })
        submission.refresh_from_db()
        self.assertEqual(submission.points_earned, 95) # Unchanged!

    def test_student_cannot_access_admin_or_teacher_portals(self):
        """Verify Student cannot access Admin or Teacher portals."""
        self.client.login(username='student1', password='password123')
        res_admin = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(res_admin.status_code, 302) # Redirected

        res_teacher = self.client.get(reverse('teacher_dashboard'))
        self.assertEqual(res_teacher.status_code, 302) # Redirected

    def test_parent_idor_isolation(self):
        """Verify Parent 1 can view linked Student 1, but passing arbitrary unlinked Student 2 ID is isolated."""
        self.client.login(username='parent1', password='password123')
        res = self.client.get(f"{reverse('parent_dashboard')}?child_id={self.student2.id}")
        self.assertContains(res, self.student1.student_id) # Falls back to Parent 1's authorized student!

    def test_unlinked_parent_never_gets_arbitrary_student(self):
        """Verify unlinked parent account never gets an arbitrary student assigned automatically."""
        unlinked_parent = User.objects.create_user(username='unlinked_parent', password='password123', email='unlinked@test.com')
        UserProfile.objects.create(user=unlinked_parent, role='parent')
        
        self.client.login(username='unlinked_parent', password='password123')
        res = self.client.get(reverse('parent_dashboard'))
        self.assertContains(res, "No Student Linked to Your Account")
        
        # Verify database was NOT modified
        self.assertEqual(Student.objects.filter(parent=unlinked_parent).count(), 0)

    def test_parent_multiple_children_context_switching(self):
        """Verify parent with multiple children can switch context between linked children only."""
        # Link student 2 to parent 1 as well
        self.student2.parent = self.parent1_user
        self.student2.save()

        self.client.login(username='parent1', password='password123')
        res1 = self.client.get(f"{reverse('parent_dashboard')}?child_id={self.student1.id}")
        self.assertContains(res1, self.student1.student_id)

        res2 = self.client.get(f"{reverse('parent_dashboard')}?child_id={self.student2.id}")
        self.assertContains(res2, self.student2.student_id)

    def test_public_signup_cannot_escalate_to_teacher_or_admin(self):
        """Verify public signup cannot register teacher or admin role."""
        res = self.client.post(reverse('signup'), {
            'firstname': 'Evil',
            'lastname': 'User',
            'email': 'evil@test.com',
            'username': 'eviluser',
            'password': 'password123',
            'confirm_password': 'password123',
            'role': 'teacher'
        }, follow=True)
        self.assertContains(res, "Security Notice")
        self.assertFalse(User.objects.filter(username='eviluser').exists())

    def test_teacher_cannot_self_assign_course(self):
        """Verify teacher cannot create or assign courses to themselves via admin endpoints."""
        self.client.login(username='teacher1', password='password123')
        res = self.client.post(reverse('admin_courses'), {
            'action': 'create_course',
            'name': 'Hacked Course',
            'code': 'HACK101',
            'instructor_id': self.instructor1.id,
            'department_id': self.dept.id
        })
        self.assertEqual(res.status_code, 302) # Redirected out of admin portal
        self.assertFalse(Course.objects.filter(code='HACK101').exists())

    def test_admin_cannot_add_exam_result(self):
        """Verify Admin cannot record exam results directly."""
        self.client.login(username='admin_test', password='password123')
        exam = Exam.objects.create(course=self.course1, title='Midterm', exam_type='midterm', exam_date='2026-12-01 10:00:00')
        res = self.client.post(reverse('admin_exams'), {
            'action': 'add_result',
            'exam_id': exam.id,
            'student_id': self.student1.id,
            'points_earned': 100
        }, follow=True)
        self.assertContains(res, "Security Policy Violation")
        self.assertFalse(ExamResult.objects.filter(exam=exam, student=self.student1).exists())

    def test_teacher_cannot_grade_unenrolled_student_in_exam(self):
        """Verify Teacher cannot record exam result for a student not enrolled in the course."""
        self.client.login(username='teacher1', password='password123')
        exam = Exam.objects.create(course=self.course1, title='Final', exam_type='final', exam_date='2026-12-15 10:00:00')
        # Student 2 is NOT enrolled in course1
        res = self.client.post(reverse('teacher_exams'), {
            'action': 'record_grade',
            'exam_id': exam.id,
            'student_id': self.student2.id,
            'points_earned': 90
        }, follow=True)
        self.assertContains(res, "is not enrolled in this course")
        self.assertFalse(ExamResult.objects.filter(exam=exam, student=self.student2).exists())

    def test_unenrolled_student_cannot_submit_assignment(self):
        """Verify Student cannot submit assignment for a course they are not enrolled in."""
        self.client.login(username='student2', password='password123')
        assignment = Assignment.objects.create(course=self.course1, title='Homework', description='Solve', due_date='2026-12-31 23:59:00')
        # Student 2 is NOT enrolled in course1
        res = self.client.post(reverse('submit_assignment', args=[assignment.id]), {
            'submission_text': 'Illegal Submission'
        }, follow=True)
        self.assertContains(res, "You are not enrolled in course")
        self.assertFalse(AssignmentSubmission.objects.filter(assignment=assignment, student=self.student2).exists())

    def test_student_cannot_read_another_users_private_message(self):
        """Verify Student 1 cannot read a private message sent to Student 2."""
        msg = Message.objects.create(sender=self.teacher1_user, recipient=self.student2_user, subject='Confidential', body='Secret content')
        self.client.login(username='student1', password='password123')
        res = self.client.get(reverse('read_message', args=[msg.id]))
        self.assertEqual(res.status_code, 404) # Direct object-level 404 rejection!

    def test_student_cannot_mark_another_users_notification_read(self):
        """Verify Student 1 cannot mark Student 2's notification as read."""
        notif = Notification.objects.create(user=self.student2_user, title='Alert', message='Personal notification')
        self.client.login(username='student1', password='password123')
        res = self.client.get(reverse('mark_notification_read', args=[notif.id]))
        self.assertEqual(res.status_code, 404) # Direct object-level 404 rejection!



