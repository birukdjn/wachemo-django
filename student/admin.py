from django.contrib import admin
from django.utils.html import format_html
import student.models as models

# Register your models here.

@admin.register(models.Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'is_active', 'created_at')
    search_fields = ('code', 'name')
    list_filter = ('is_active', 'created_at')
    ordering = ('code',)

@admin.register(models.Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'get_full_name', 'department', 'phone', 'is_active')
    search_fields = ('employee_id', 'user__first_name', 'user__last_name', 'user__email')
    list_filter = ('department', 'is_active', 'hire_date')
    list_select_related = ('user', 'department')
    ordering = ('employee_id',)
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'employee_id', 'phone', 'address')
        }),
        ('Professional Information', {
            'fields': ('department', 'office_location', 'specialization', 'qualification', 'hire_date')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

@admin.register(models.Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'get_full_name', 'department', 'status', 'gpa', 'credits_completed')
    search_fields = ('student_id', 'user__first_name', 'user__last_name', 'user__email')
    list_filter = ('department', 'status', 'enrollment_date', 'graduation_date')
    list_select_related = ('user', 'department')
    ordering = ('student_id',)
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'student_id', 'phone', 'address', 'date_of_birth')
        }),
        ('Academic Information', {
            'fields': ('department', 'enrollment_date', 'graduation_date', 'status', 'gpa', 'credits_completed', 'credits_required')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact', 'emergency_phone')
        }),
    )

@admin.register(models.Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'instructor', 'department', 'credits', 'semester', 'is_active')
    search_fields = ('code', 'name', 'description')
    list_filter = ('department', 'instructor', 'is_active', 'is_featured', 'semester', 'academic_year')
    list_select_related = ('instructor', 'department')
    ordering = ('code',)
    filter_horizontal = ('prerequisites',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'description', 'credits')
        }),
        ('Instructor & Department', {
            'fields': ('instructor', 'department')
        }),
        ('Course Details', {
            'fields': ('prerequisites', 'max_students', 'semester', 'academic_year')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
    )

@admin.register(models.Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'semester', 'academic_year', 'grade', 'is_active')
    search_fields = ('student__student_id', 'student__user__first_name', 'student__user__last_name', 'course__code', 'course__name')
    list_filter = ('semester', 'academic_year', 'is_active', 'enrollment_date')
    list_select_related = ('student__user', 'course')
    ordering = ('-enrollment_date',)

@admin.register(models.Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'due_date', 'max_points', 'is_published')
    search_fields = ('title', 'course__code', 'course__name')
    list_filter = ('course', 'is_published', 'due_date', 'created_at')
    list_select_related = ('course',)
    ordering = ('-due_date',)

@admin.register(models.AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'submitted_at', 'points_earned', 'is_graded')
    search_fields = ('student__student_id', 'student__user__first_name', 'assignment__title')
    list_filter = ('is_graded', 'submitted_at', 'assignment__course')
    list_select_related = ('student__user', 'assignment__course')
    ordering = ('-submitted_at',)

@admin.register(models.Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'date', 'status', 'marked_by')
    search_fields = ('student__student_id', 'student__user__first_name', 'course__code')
    list_filter = ('status', 'date', 'course', 'marked_by')
    list_select_related = ('student__user', 'course', 'marked_by__user')
    ordering = ('-date',)

@admin.register(models.Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'exam_type', 'exam_date', 'max_points', 'is_published')
    search_fields = ('title', 'course__code', 'course__name')
    list_filter = ('exam_type', 'is_published', 'exam_date', 'course')
    list_select_related = ('course',)
    ordering = ('-exam_date',)

@admin.register(models.ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'points_earned', 'grade', 'is_published')
    search_fields = ('student__student_id', 'student__user__first_name', 'exam__title')
    list_filter = ('is_published', 'exam__exam_type', 'exam__course')
    list_select_related = ('student__user', 'exam__course')
    ordering = ('-created_at',)

@admin.register(models.Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'total_copies', 'available_copies', 'is_active')
    search_fields = ('title', 'author', 'isbn')
    list_filter = ('category', 'is_active', 'publication_year')
    ordering = ('title',)

@admin.register(models.BookBorrowing)
class BookBorrowingAdmin(admin.ModelAdmin):
    list_display = ('student', 'book', 'borrowed_date', 'due_date', 'status', 'fine_amount')
    search_fields = ('student__student_id', 'student__user__first_name', 'book__title')
    list_filter = ('status', 'borrowed_date', 'due_date')
    list_select_related = ('student__user', 'book')
    ordering = ('-borrowed_date',)

@admin.register(models.Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'target_audience', 'department', 'is_published', 'publish_date')
    search_fields = ('title', 'content')
    list_filter = ('priority', 'target_audience', 'department', 'is_published', 'publish_date')
    list_select_related = ('department', 'created_by')
    ordering = ('-publish_date',)
    fieldsets = (
        ('Content', {
            'fields': ('title', 'content', 'priority')
        }),
        ('Target Audience', {
            'fields': ('target_audience', 'department')
        }),
        ('Publishing', {
            'fields': ('is_published', 'publish_date', 'expiry_date', 'created_by')
        }),
    )

@admin.register(models.Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'title')
    list_filter = ('notification_type', 'is_read', 'created_at')
    list_select_related = ('user',)
    ordering = ('-created_at',)
    