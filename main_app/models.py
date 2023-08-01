from django.db import models
from django.urls import reverse
from datetime import date
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser


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
