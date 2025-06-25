from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


# Create your models here.
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