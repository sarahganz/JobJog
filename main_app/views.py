import os
import uuid
import boto3
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from .models import Employer, CustomUser, Employee, Shift, EmployeeAssignment, Job
from datetime import datetime
from .forms import (
    JobAssignmentForm,
    EmployeeRegistrationForm,
    InviteEmployeeForm,
    EmployerRegistrationForm,
    EmployerLoginForm,
)
from django.utils import timezone
from .models import Job


def home(request):
    return render(request, "home.html")


def about(request):
    return render(request, "about.html")


def employer_registration(request):
    if request.method == "POST":
        form = EmployerRegistrationForm(request.POST)
        if form.is_valid():
            company_name = form.cleaned_data["company_name"]
            user = form.save()

            # Check if an Employer object already exists for the user
            employer, created = Employer.objects.get_or_create(
                user=user, defaults={"company_name": company_name}
            )

            if not created:
                # If the Employer object already existed, update the company_name
                employer.company_name = company_name
                employer.save()

            # Log in the employer after successful registration
            login(request, user)

            return redirect("employer_dashboard")
    else:
        form = EmployerRegistrationForm()

    return render(request, "employer/registration.html", {"form": form})


def employer_login(request):
    if request.method == "POST":
        form = EmployerLoginForm(request, request.POST)
        if form.is_valid():
            email = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            # Authenticate employer
            user = authenticate(request, username=email, password=password)

            if user is not None and user.is_employer:
                # If the user is an employer and the provided credentials are valid, log in the employer
                login(request, user)
                return redirect("employer_dashboard")
            else:
                # If the provided credentials are invalid or the user is not an employer,
                # display an error message
                form.add_error("username", "Invalid email or password.")
    else:
        form = EmployerLoginForm()

    return render(request, "employer_login.html", {"form": form})


@login_required
def employer_dashboard(request):
    # Retrieve the logged-in employer's data
    employer = request.user.employer

    # Get the list of employees associated with the employer
    employees = employer.employee_set.all()

    context = {
        "employer": employer,
        "employees": employees,
    }

    return render(request, "employer_dashboard.html", context)


def invite_employee(request):
    if request.method == "POST":
        form = InviteEmployeeForm(request.POST)
        if form.is_valid():
            # Get the email address entered in the form
            employee_email = form.cleaned_data["employee_email"]

            # Your logic to send the invite email here
            # Use the send_mail function to send the email
            # Example usage:
            subject = "Invitation to join our company"
            message = "You have been invited to join our company. Click on the link to register."
            from_email = "noreply@example.com"
            recipient_list = [employee_email]

            send_mail(subject, message, from_email, recipient_list)

            return redirect(
                "employer_dashboard"
            )  # Redirect to employer dashboard after sending the invite
    else:
        form = InviteEmployeeForm()

    return render(request, "invite_employee.html", {"form": form})


def employee_registration(request, token):
    # Here, you can handle the logic to validate the token and retrieve the associated employer
    # Once validated, the employee can proceed with the registration process
    if request.method == "POST":
        form = EmployeeRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            employer = ...  # Retrieve the employer associated with the token
            Employee.objects.create(user=user, employer=employer)
            login(request, user)  # Log in the employee after successful registration
            return redirect(
                "employee_dashboard"
            )  # Redirect to employee dashboard after registration
    else:
        form = EmployeeRegistrationForm()

    return render(request, "employee_registration.html", {"form": form})


@login_required
def employee_dashboard(request):
    employee = request.user.employee
    assigned_jobs = EmployeeAssignment.objects.filter(employee=employee)

    context = {
        "employee": employee,
        "assigned_jobs": assigned_jobs,
    }

    return render(request, "employee_dashboard.html", context)


@login_required
def clock_in(request):
    employee = request.user.employee
    shift = Shift.objects.create(employee=employee, clock_in=datetime.now())
    return redirect("employee_dashboard")


@login_required
def clock_out(request):
    employee = request.user.employee
    shift = Shift.objects.filter(employee=employee, clock_out__isnull=True).first()
    if shift:
        shift.clock_out = datetime.now()
        shift.save()
    return redirect("employee_dashboard")


def job_assignment(request):
    if request.method == "POST":
        form = JobAssignmentForm(request.POST)
        if form.is_valid():
            job = form.save()
            return redirect(
                "employer_dashboard"
            )  # Redirect to employer dashboard after successful assignment
    else:
        form = JobAssignmentForm()

    return render(request, "job_assignment.html", {"form": form})


@login_required
def clock_in(request, assignment_id):
    assignment = EmployeeAssignment.objects.get(pk=assignment_id)

    if assignment.clock_in is None:
        assignment.clock_in = timezone.now()
        assignment.save()

    return redirect("employee_dashboard")


@login_required
def clock_out(request, assignment_id):
    assignment = EmployeeAssignment.objects.get(pk=assignment_id)

    if assignment.clock_out is None and assignment.clock_in is not None:
        assignment.clock_out = timezone.now()
        assignment.save()

    return redirect("employee_dashboard")


@login_required
def job_details(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    return render(request, "job_details.html", {"job": job})


def jobs_detail(request, job_id):
  job = Job.objects.get(id=job_id)
  return render(request, 'jobs/detail.html', { 'job': job })

def jobs_index(request):
  jobs = Job.objects.all()
  return render(request, 'jobs/index.html', {
    'jobs': jobs
  })

class JobCreate(CreateView):
  model = Job
  fields = ['description', 'address', 'date', 'time', 'status']

class JobUpdate(UpdateView):
  model = Job
  fields = ['description', 'address', 'date', 'time', 'status']

class JobDelete(DeleteView):
  model = Job
  success_url = '/jobs'

