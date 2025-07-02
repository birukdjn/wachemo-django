from django.contrib import admin
from .models import News, Gallery ,Event,  UserProfile
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


# Register your models here.
 

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'reporter', 'day', 'month')
    search_fields = ('title', 'reporter')
    list_filter = ('date',)
    ordering = ('-date',)
    date_hierarchy = 'date'
    
@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('description',)
    search_fields = ('description',)
    ordering = ('-id',)    
    
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'day', 'month', 'location')
    search_fields = ('title', 'location')
    list_filter = ('day', 'month')
    ordering = ('-day', '-month')



# UserProfile Admin
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_info', 'role', 'role_specific_info')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email', 'student_id', 'parent_phone')
    
    def user_info(self, obj):
        return f"{obj.user.username} ({obj.user.get_full_name()})"
    user_info.short_description = 'User'
    
    def role_specific_info(self, obj):
        if obj.role == 'student':
            return obj.student_id
        elif obj.role == 'teacher':
            return obj.teacher_subject
        elif obj.role == 'parent':
            return obj.parent_phone
        return ""
    role_specific_info.short_description = 'Role Info'

# Custom User Admin with inline profile
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('role', 'student_id', 'teacher_subject', 'parent_phone')

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff')
    
    def get_role(self, obj):
        return obj.userprofile.role if hasattr(obj, 'userprofile') else None
    get_role.short_description = 'Role'
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

# Unregister default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)