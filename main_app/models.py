from django.db import models
from django.urls import reverse
from datetime import date
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser

STATUSES = (
    ("Incomplete", "Incomplete"),
    ("Complete", "Complete"),
)


class CustomUser(AbstractUser):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
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
    description = models.CharField(max_length=250)
    address = models.CharField(max_length=250)
    date = models.DateField("Job Date")
    time = models.TimeField(("Job Time"), blank=True)
    status = models.CharField(max_length=10, choices=STATUSES, default=STATUSES[0][0])
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.description} ({self.id})"

    def get_absolute_url(self):
        return reverse("detail", kwargs={"job_id": self.id})


class EmployeeAssignment(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    clock_in = models.DateTimeField(null=True, blank=True)
    clock_out = models.DateTimeField(null=True, blank=True)


class EmployeeInvitation(models.Model):
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    token = models.CharField(max_length=32, unique=True)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"EmployeeInvitation from {self.employer} to {self.email}"


class Photo(models.Model):
    url = models.CharField(max_length=200)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)

    def __str__(self):
        return f"Photo for job_id: {self.job_id} @{self.url}"
