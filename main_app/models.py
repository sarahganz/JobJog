from django.db import models
from django.urls import reverse
from datetime import date
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser


STATUS_CHOICES = (
        ('I', 'Incomplete'),
        ('C', 'Complete'),
    )

class CustomUser(AbstractUser):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone_number = models.CharField(max_length=10)


class Employer(models.Model):
    user = models.OneToOneField("CustomUser", on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100)


class Employee(models.Model):
    user = models.OneToOneField("CustomUser", on_delete=models.CASCADE)
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    skills = models.CharField(max_length=100)
    hourly_rate = models.IntegerField()

class Job(models.Model):
    description = models.CharField(max_length=260)
    address = models.CharField(max_length=250)
    date = models.DateField('Job Date')
    time = models.TimeField((u"Job Time"), blank=True)
    status = models.CharField(
        max_length=1,  
        choices=STATUS_CHOICES,
        default=STATUS_CHOICES[0][0],  
    )

    def __str__(self):
        return f'{self.description} ({self.id})'
    
    def get_absolute_url(self):
        return reverse('detail', kwargs={'job_id': self.id})

