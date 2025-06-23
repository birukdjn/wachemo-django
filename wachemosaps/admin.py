from django.contrib import admin
from .models import news

# Register your models here.

@admin.register(news)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'reporter', 'day', 'month')
    search_fields = ('title', 'reporter')
    list_filter = ('date',)
    ordering = ('-date',)
    date_hierarchy = 'date'