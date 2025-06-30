from django.contrib import admin
from .models import News, Gallery ,Event

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
