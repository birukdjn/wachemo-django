from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User

# Create your models here



class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    reporter = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    day = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(31)])
    MONTH_CHOICES = [
        ('Jan', 'January'),
        ('Feb', 'February'),
        ('Mar', 'March'),
        ('Apr', 'April'),
        ('May', 'May'),
        ('Jun', 'June'),
        ('Jul', 'July'),
        ('Aug', 'August'),
        ('Sep', 'September'),
        ('Oct', 'October'),
        ('Nov', 'November'),
        ('Dec', 'December'),
    ]
    month = models.CharField(max_length=3, choices=MONTH_CHOICES)
    image = models.URLField(max_length=200, blank=True, null=True)
     
class Gallery(models.Model):
    image = models.URLField(max_length=200, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.description if self.description else "Gallery Image"
    
    
class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    day = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(31)])
    MONTH_CHOICES = [
        ('Jan', 'January'),
        ('Feb', 'February'),
        ('Mar', 'March'),
        ('Apr', 'April'),
        ('May', 'May'),
        ('Jun', 'June'),
        ('Jul', 'July'),
        ('Aug', 'August'),
        ('Sep', 'September'),
        ('Oct', 'October'),
        ('Nov', 'November'),
        ('Dec', 'December'),
    ]
    month = models.CharField(max_length=3, choices=MONTH_CHOICES)
    location = models.CharField(max_length=200, blank=True, null=True)
    duration = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.title
    
    

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('parent', 'Parent'),
        ('teacher', 'Teacher'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    
    # Optional role-specific fields
    student_id = models.CharField(max_length=20, blank=True, null=True)
    teacher_subject = models.CharField(max_length=50, blank=True, null=True)
    parent_phone = models.CharField(max_length=15, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"