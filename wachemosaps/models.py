from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError


# Create your models here.
class news(models.Model):
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