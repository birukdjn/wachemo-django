from datetime import date
from typing import List, Dict, Any
from django.db import transaction
from django.core.exceptions import ValidationError
from student.models import Student, Course, Instructor, Attendance, Enrollment

class AttendanceService:
    @staticmethod
    @transaction.atomic
    def record_bulk_attendance(instructor: Instructor, course: Course, record_date: date, records: List[Dict[str, Any]]) -> int:
        """
        Atomically records attendance for enrolled students in an instructor's course.
        """
        if course.instructor != instructor and not instructor.user.is_superuser:
            raise ValidationError("Instructor is not authorized for this course.")

        enrolled_student_ids = set(
            Enrollment.objects.filter(course=course, is_active=True).values_list('student_id', flat=True)
        )

        saved_count = 0
        for item in records:
            student_id = item.get('student_id')
            status = item.get('status', 'present')
            notes = item.get('notes', '')

            if student_id not in enrolled_student_ids:
                continue

            Attendance.objects.update_or_create(
                student_id=student_id,
                course=course,
                date=record_date,
                defaults={
                    'status': status,
                    'notes': notes,
                    'marked_by': instructor
                }
            )
            saved_count += 1

        return saved_count
