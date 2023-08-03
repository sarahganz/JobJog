import os
import uuid
import boto3
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
import random
import string
from django.contrib.auth import get_user_model
from .models import (
    Employer,
    CustomUser,
    Employee,
    EmployeeAssignment,
    Job,
    EmployeeInvitation,
)
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
from django.urls import reverse
from django.core import signing
from django.contrib.sites.shortcuts import get_current_site
from django.http import Http404
from django.utils.crypto import get_random_string
from django.http import HttpResponse
from django.utils.crypto import get_random_string


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

            if user is not None:
                # Check if the user has an associated employer instance
                employer = Employer.objects.filter(user=user).first()

                if employer:
                    # If the user is associated with an employer and the provided credentials are valid,
                    # log in the employer
                    login(request, user)
                    return redirect("employer_dashboard")
                else:
                    # If the user is not associated with an employer, display an error message
                    form.add_error("username", "You are not authorized as an employer.")
            else:
                # If the provided credentials are invalid, display an error message
                form.add_error("username", "Invalid email or password.")
    else:
        form = EmployerLoginForm()

    return render(request, "employer_login.html", {"form": form})


def employer_logout(request):
    logout(request)
    return redirect("home")


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


def generate_token():
    return "".join(random.choices(string.ascii_letters + string.digits, k=32))


@login_required
def invite_employee(request):
    if request.method == "POST":
        form = InviteEmployeeForm(request.POST)
        if form.is_valid():
            # Get the email address entered in the form
            employee_email = form.cleaned_data["employee_email"]

            # Generate a unique token for the employee invitation
            token = generate_token()

            # Save the token in the database along with the employer information
            EmployeeInvitation.objects.create(
                employer=request.user.employer,  # Use request.user.employer
                token=token,
                email=employee_email,
            )

            # Send the email/notification with the invite link to the employee
            invite_link = f"http://{request.get_host()}/employee/registration/{token}/"

            # You can use a library like Django's built-in email support or a third-party library to send the email here

            # Optionally, you can display the link to the employer for copying
            print("Invite Link:", invite_link)

            context = {
                "form": form,
                "invite_link": invite_link,
            }

            return render(request, "invite_employee.html", context)
    else:
        form = InviteEmployeeForm()

    return render(request, "invite_employee.html", {"form": form})


def employee_registration(request, token):
    try:
        invitation = EmployeeInvitation.objects.get(token=token)
    except EmployeeInvitation.DoesNotExist:
        return HttpResponse("Invalid token")

    User = get_user_model()

    if request.method == "POST":
        form = EmployeeRegistrationForm(request.POST)
        if form.is_valid():
            # Create the user account
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )

            # Create the employee profile
            employee = Employee.objects.create(
                user=user,
                email=invitation.email,
                # You can set other fields here based on the registration form
            )

            # Optionally, you can clear the invitation after successful registration
            invitation.delete()

            return render(request, "registration_success.html")
    else:
        form = EmployeeRegistrationForm()

    return render(request, "employee_registration.html", {"form": form})


@login_required
def clock_out(request):
    employee = request.user.employee

    # Find the latest assignment with NULL clock_out value for the employee
    assignment = EmployeeAssignment.objects.filter(
        employee=employee, clock_out__isnull=True
    ).latest("clock_in")

    if assignment and assignment.clock_in:
        # If a valid assignment is found, update its clock_out value
        assignment.clock_out = datetime.now()
        assignment.save()

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
def add_photo(request, job_id):
  # photo-file maps to the "name" attr on the <input>
  photo_file = request.FILES.get('photo-file', None)
  if photo_file:
    s3 = boto3.client('s3')
    # Need a unique "key" (filename)
    # It needs to keep the same file extension
    # of the file that was uploaded (.png, .jpeg, etc.)
    key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
    try:
      bucket = os.environ['S3_BUCKET']
      s3.upload_fileobj(photo_file, bucket, key)
      url = f"{os.environ['S3_BASE_URL']}{bucket}/{key}"
      Photo.objects.create(url=url, job_id=job_id)
    except Exception as e:
      print('An error occurred uploading file to S3')
      print(e)
  return redirect('detail', job_id=job_id)



@login_required
def job_details(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    return render(request, "job_details.html", {"job": job})


def jobs_detail(request, job_id):
    job = Job.objects.get(id=job_id)
    return render(request, "jobs/detail.html", {"job": job})


def jobs_index(request):
    jobs = Job.objects.all()
    return render(request, "jobs/index.html", {"jobs": jobs})


class JobCreate(CreateView):
    model = Job
    fields = ["description", "address", "date", "time", "status"]


class JobUpdate(UpdateView):
    model = Job
    fields = ["description", "address", "date", "time", "status"]


class JobDelete(DeleteView):
    model = Job
    success_url = "/jobs"
