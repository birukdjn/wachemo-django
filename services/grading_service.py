from django.db import transaction
from django.db.models import Avg, Sum
from student.models import Enrollment, ExamResult, AssignmentSubmission, Student, Course

class GradingService:
    @staticmethod
    def calculate_letter_grade(percentage: float) -> str:
        if percentage >= 90:
            return 'A'
        elif percentage >= 80:
            return 'B'
        elif percentage >= 70:
            return 'C'
        elif percentage >= 60:
            return 'D'
        else:
            return 'F'

    @classmethod
    @transaction.atomic
    def update_course_grade(cls, student: Student, course: Course) -> str:
        """
        Calculates and updates final course letter grade based on published assessments.
        """
        exam_results = ExamResult.objects.filter(
            student=student,
            exam__course=course,
            is_published=True
        )
        total_points = exam_results.aggregate(total=Sum('points_earned'))['total'] or 0
        total_max = sum(er.exam.max_points for er in exam_results) or 100

        percentage = (total_points / total_max) * 100 if total_max > 0 else 0
        letter_grade = cls.calculate_letter_grade(percentage)

        enrollment = Enrollment.objects.filter(student=student, course=course).first()
        if enrollment:
            enrollment.grade = letter_grade
            enrollment.save()

        return letter_grade
