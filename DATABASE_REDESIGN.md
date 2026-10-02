# WSaPS Database Architecture Redesign & Extension Specification

## Executive Summary
This document specifies the enterprise database architecture redesign for the **Wachemo Secondary & Preparatory School Management System (WSaPS)**. The redesign optimizes domain boundaries, enforces transactional integrity, adds indexing for high-frequency queries, implements explicit constraints, and introduces domain service layers while ensuring 100% backward compatibility with all existing APIs, templates, URLs, and RBAC rules.

---

## 1. Domain Architecture & Relationships

```
                     +-------------------+
                     |    auth.User      |
                     +-------------------+
                       |    |         |
          +------------+    |         +----------------+
          | (1:1)           | (1:1)                    | (1:1)
          v                 v                          v
  +---------------+  +--------------+          +----------------+
  |  UserProfile  |  |  Instructor  |          |    Student     |
  +---------------+  +--------------+          +----------------+
                            | (1:N)                    |        |
                            v                          |        |
                       +---------+                     |        |
                       | Course  |<--------------------+ (M:N via| Enrollment)
                       +---------+                              |
                       |    |                                   |
              +--------+    +-------------+                     |
              | (1:N)                     | (1:N)               |
              v                           v                     v
       +------------+              +------------+       +-------------------+
       | Assignment |              |    Exam    |       |   Attendance      |
       +------------+              +------------+       +-------------------+
              |                           |
              v (1:N)                     v (1:N)
   +--------------------+        +------------------+
   |AssignmentSubmission|        |    ExamResult    |
   +--------------------+        +------------------+
```

---

## 2. Target Models & Enhancements

### A. UserProfile Model (`wachemosaps.UserProfile`)
- **Fields**: `user` (1:1), `role` (`student`, `parent`, `teacher`, `admin`), `student_id`, `teacher_subject`, `parent_phone`, `created_at`, `updated_at`.
- **RBAC Rule**: Self-provisioning of `admin` or `teacher` roles via public endpoints is forbidden.

### B. Student Model (`student.Student`)
- **Fields**: `user` (1:1), `parent` (FK to `User`, `null=True`, `on_delete=SET_NULL`), `student_id` (unique), `department` (FK), `phone`, `address`, `date_of_birth`, `enrollment_date`, `graduation_date`, `status`, `gpa`, `credits_completed`, `credits_required`, `emergency_contact`, `emergency_phone`, `created_at`, `updated_at`.
- **Security Rule**: Parents only access explicitly linked children (`Student.objects.filter(parent=request.user)`).

### C. Instructor Model (`student.Instructor`)
- **Fields**: `user` (1:1), `employee_id` (unique), `department` (FK), `phone`, `office_location`, `specialization`, `qualification`, `hire_date`, `is_active`, `created_at`, `updated_at`.
- **RBAC Rule**: Course assignment is strictly an administrative function.

### D. Department Model (`student.Department`)
- **Fields**: `name` (unique), `code` (unique), `description`, `is_active`, `created_at`, `updated_at`.

### E. Course Model (`student.Course`)
- **Fields**: `code` (unique), `name`, `instructor` (FK), `department` (FK), `credits`, `prerequisites` (M2M), `max_students`, `semester`, `academic_year`, `is_active`, `is_featured`, `created_at`, `updated_at`.

### F. Enrollment Model (`student.Enrollment`)
- **Fields**: `student` (FK), `course` (FK), `enrollment_date`, `grade`, `semester`, `academic_year`, `is_active`, `created_at`, `updated_at`.
- **Constraints**: `UniqueConstraint(fields=['student', 'course', 'semester', 'academic_year'], name='unique_student_course_period')`.
- **Indexes**: `(student, course)`, `(student, semester, academic_year)`, `(course, semester, academic_year)`.

### G. Assessment & Grading Models (`Assignment`, `AssignmentSubmission`, `Exam`, `ExamResult`)
- **Constraints**:
  - `AssignmentSubmission`: `UniqueConstraint(fields=['assignment', 'student'], name='unique_assignment_student_submission')`.
  - `ExamResult`: `UniqueConstraint(fields=['exam', 'student'], name='unique_exam_student_result')`.
- **Integrity Rule**: Only instructors assigned to the course can grade submissions/exams for enrolled students.

### H. Attendance Model (`student.Attendance`)
- **Constraints**: `UniqueConstraint(fields=['student', 'course', 'date'], name='unique_student_course_attendance_date')`.
- **Indexes**: `(student, course, date)`.

---

## 3. Database Indexing & Optimization Strategy

The following composite database indexes are added:
1. `Enrollment`: `(student, course)`, `(student, semester, academic_year)`, `(course, semester, academic_year)`
2. `AssignmentSubmission`: `(assignment, student)`
3. `ExamResult`: `(exam, student)`
4. `Attendance`: `(student, course, date)`
5. `Message`: `(sender, recipient)`, `(recipient, is_read)`
6. `Notification`: `(user, is_read)`

---

## 4. Service Abstraction Layer

To ensure transaction safety (`transaction.atomic()`) and prevent partial database writes, the following domain services are established:
- `services/enrollment_service.py`: Enrolls students safely with capacity check and unique period validation.
- `services/grading_service.py`: Computes course final grades from published assignments and exams.
- `services/parent_service.py`: Handles secure parent-child lookup without side effects.
- `services/attendance_service.py`: Processes bulk attendance records atomically.
- `services/messaging_service.py`: Enforces server-controlled sender attribution.

---

## 5. Security & RBAC Enforcement Summary

| Role | Permissions & Boundaries |
| :--- | :--- |
| **Admin** | Full system governance, user management, course setup, teacher assignment, library/club setup. |
| **Teacher** | Grade & mark attendance for **assigned courses only**. Cannot self-assign courses or grade unenrolled students. |
| **Student** | Read-only access to own grades/attendance/schedule; submit assignments for active enrollments. |
| **Parent** | Read-only access to **explicitly linked children only** (`parent=request.user`). No fallback to arbitrary students. |

---

## 6. Migration & Rollback Strategy

1. **Phase 1**: Add optional/nullable `updated_at` fields and `Meta.constraints` / `Meta.indexes`.
2. **Phase 2**: Generate Django migrations via `python manage.py makemigrations`.
3. **Phase 3**: Verify data integrity using `python manage.py test`.
4. **Rollback Procedure**: In case of deployment rollback, standard Django reverse migration commands (`python manage.py migrate <app> <previous_migration>`) can be safely executed without data loss.
