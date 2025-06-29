from django.contrib import admin
import student.models as models

# Register your models here.

@admin.register(models.Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name')
    search_fields = ('first_name', 'last_name')
    
@admin.register(models.Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'instructor', 'credits', 'is_active')
    search_fields = ('code', 'name')
    list_filter = ('is_active',)
    list_select_related = ('instructor',)   
    ordering = ('code',)
    fieldsets = (
        (None, {
            'fields': ('code', 'name', 'instructor', 'credits', 'is_active')
        }),
    )   
    