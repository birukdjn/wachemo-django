from django.db import models

# Create your models here.
class news(models.Model):
    title = models.CharField(max_length=200)
    image= models.ImageField(upload_to='images/', blank=True, null=True)
    content = models.TextField()
    reporter = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    day= models.FloatField(max_length=2)
    month= models.CharField( max_length=4)
    