from django.contrib import admin
from .models import News, Gallery

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