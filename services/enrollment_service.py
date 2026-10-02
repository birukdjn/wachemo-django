from django.db import transaction
from django.core.exceptions import ValidationError
from student.models import Student, Course, Enrollment

class EnrollmentService:
    @staticmethod
    @transaction.atomic
    def enroll_student(student: Student, course: Course, semester: str = "", academic_year: str = "") -> Enrollment:
        """
        Enrolls a student in a course atomically, enforcing maximum class capacity
        and unique period constraints.
        """
        if not course.is_active:
            raise ValidationError("Cannot enroll in an inactive course.")
            
        current_count = Enrollment.objects.filter(course=course, is_active=True).count()
        if current_count >= course.max_students:
            raise ValidationError(f"Course capacity limit ({course.max_students}) reached.")

        existing = Enrollment.objects.filter(
            student=student,
            course=course,
            semester=semester or course.semester,
            academic_year=academic_year or course.academic_year
        ).first()

        if existing:
            if not existing.is_active:
                existing.is_active = True
                existing.save()
            return existing

        enrollment = Enrollment.objects.create(
            student=student,
            course=course,
            semester=semester or course.semester,
            academic_year=academic_year or course.academic_year,
            is_active=True
        )
        return enrollment
