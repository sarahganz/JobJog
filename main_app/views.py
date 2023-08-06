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
    Photo,
)
from datetime import datetime
from .forms import (
    JobAssignmentForm,
    EmployeeRegistrationForm,
    InviteEmployeeForm,
    EmployerRegistrationForm,
    EmployerLoginForm,
    EmployeeLoginForm,
    AssignEmployeeForm,
    CustomEmployeeUpdateForm,
)

from .models import Job
from django.urls import reverse
from django.core import signing
from django.contrib.sites.shortcuts import get_current_site
from django.http import Http404
from django.utils.crypto import get_random_string
from django.http import HttpResponse
from django.utils.crypto import get_random_string
from django.forms import ModelChoiceField
from django.utils import timezone
from datetime import timedelta


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


def employee_login(request):
    if request.method == "POST":
        form = EmployeeLoginForm(request, request.POST)
        if form.is_valid():
            email = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            # Authenticate employer
            user = authenticate(request, username=email, password=password)

            if user is not None:
                # Check if the user has an associated employee instance
                employee = Employee.objects.filter(user=user).first()

                if employee:
                    # If the user is associated with an employee and the provided credentials are valid,
                    # log in the employee
                    login(request, user)
                    return redirect("employee_dashboard")
                else:
                    # If the user is not associated with an employee, display an error message
                    form.add_error("username", "You are not authorized as an employee.")
            else:
                # If the provided credentials are invalid, display an error message
                form.add_error("username", "Invalid email or password.")
    else:
        form = EmployeeLoginForm()

    return render(request, "employee_login.html", {"form": form})


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

    if request.method == "POST":
        form = EmployeeRegistrationForm(request.POST)
        if form.is_valid() and form.cleaned_data["email"] == invitation.email:
            invitation = EmployeeInvitation.objects.get(token=token)
            # Create the user account
            hourly_rate = form.cleaned_data["hourly_rate"]
            skills = form.cleaned_data["skills"]
            print("before user save line 183")
            form.employer = invitation.employer
            print(form)
            user = form.save()
            print("after user save line 185")
            print(user)
            employee, created = Employee.objects.get_or_create(
                user=user,
                employer=invitation.employer,
                hourly_rate=hourly_rate,
                skills=skills,
            )
            print("after line 186")
            if not created:
                employee.hourly_rate = hourly_rate
                employee.skills = skills
                employee.employer = invitation.employer.id
                employee.save()
            employer = invitation.employer
            # Create the employee profile
            # employee = Employee.objects.create(
            #     user=user,
            #     email=invitation.email,
            #     employer=employer,
            #     hourly_rate=hourly_rate,
            #     skills=skills,
            # )
            print(employee)
            return redirect("employee_dashboard")
    else:
        form = EmployeeRegistrationForm()

    return render(request, "employee_registration.html", {"form": form})


@login_required
def employee_dashboard(request):
    # Retrieve the logged-in employer's data
    employee = request.user.employee

    # Get the list of employees associated with the employer

    context = {
        "employee": employee,
    }

    return render(request, "employee_dashboard.html", context)


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


def clock_out(request, assignment_id):
    assignment = get_object_or_404(EmployeeAssignment, id=assignment_id)
    if assignment.clock_in and not assignment.clock_out:
        assignment.clock_out = timezone.now() - timedelta(hours=4)
        assignment.save()
    return redirect("job_details", job_id=assignment.job.id)

@login_required
def clock_in(request, assignment_id):
    assignment = get_object_or_404(EmployeeAssignment, id=assignment_id)
    if assignment.clock_in is None:
        assignment.clock_in = timezone.now() - timedelta(hours=4)
        assignment.save()
    return redirect("job_details", job_id=assignment.job.id)

@login_required
def add_photo(request, job_id):
    # Get the current employee who is uploading the photo
    employee = request.user.employee

    # photo-file maps to the "name" attr on the <input>
    photo_file = request.FILES.get("photo-file", None)
    if photo_file:
        s3 = boto3.client("s3")
        key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind(".") :]
        try:
            bucket = os.environ["S3_BUCKET"]
            s3.upload_fileobj(photo_file, bucket, key)
            url = f"{os.environ['S3_BASE_URL']}{bucket}/{key}"

            # Save the photo with the uploaded_by field and timestamp
            Photo.objects.create(url=url, job_id=job_id, uploaded_by=employee)
        except Exception as e:
            print("An error occurred uploading file to S3")
            print(e)
    return redirect("job_details", job_id=job_id)


@login_required
def job_details(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    employee = request.user.employee

    # Retrieve the assignment for the given job and employee
    assignment = EmployeeAssignment.objects.filter(employee=employee, job=job).first()

    return render(request, "job_details.html", {"job": job, "assignment": assignment})


def jobs_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    employee_assignments = EmployeeAssignment.objects.filter(job=job)
    assigned_employees = [assignment.employee for assignment in employee_assignments]
    return render(
        request,
        "jobs/detail.html",
        {"job": job, "assigned_employees": assigned_employees},
    )


def jobs_index(request):
    print(request.user.id)
    jobs = Job.objects.filter(employer=request.user.employer)
    return render(request, "jobs/index.html", {"jobs": jobs})


class JobCreate(CreateView):
    model = Job
    fields = ["description", "address", "date", "time", "status"]

    def form_valid(self, form):
        # Get the logged-in employer and assign it to the job
        form.instance.employer = self.request.user.employer

        # Call the parent class's form_valid method to save the job to the database
        return super().form_valid(form)


from django.contrib.auth.forms import UserChangeForm


class CustomEmployeeUpdateForm(UserChangeForm):
    class Meta:
        model = Employee
        fields = ["skills", "hourly_rate"]


class EmployeeUpdate(UpdateView):
    model = Employee
    form_class = CustomEmployeeUpdateForm
    template_name = "employee_update_form.html"


class JobDelete(DeleteView):
    model = Job
    success_url = "/jobs"


def employees_index(request):
    employees = Employee.objects.filter(employer=request.user.employer)

    return render(request, "employee_index.html", {"employees": employees})


def detail_employee(request, employee_id):
    # Get the employee object using the provided employee_id
    employee = get_object_or_404(Employee, id=employee_id)

    return render(request, "employee_detail.html", {"employee": employee})


def assign_employee_to_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    available_employees = Employee.objects.filter(
        employer=request.user.employer
    ).exclude(employeeassignment__job=job)
    assigned_employees = job.employeeassignment_set.all()

    if request.method == "POST":
        employee_id = request.POST.get("employee_id")
        action = request.POST.get("action")

        if action == "assign":
            employee = get_object_or_404(Employee, id=employee_id)
            assignment = EmployeeAssignment(employee=employee, job=job)
            assignment.save()
        elif action == "remove":
            assignment = EmployeeAssignment.objects.get(
                employee_id=employee_id, job=job
            )
            assignment.delete()

    context = {
        "job": job,
        "available_employees": available_employees,
        "assigned_employees": assigned_employees,
    }

    return render(request, "assign_employee_to_job.html", context)


class EmployeeUpdate(UpdateView):
    model = Employee
    form_class = CustomEmployeeUpdateForm
    template_name = "employee_update_form.html"


class EmployeeDelete(DeleteView):
    model = Employee
    success_url = "/employees"


def employee_assignments(request, employee_id):
    employee = Employee.objects.get(pk=employee_id)
    print(employee)
    assignments = EmployeeAssignment.objects.filter(employee=employee)
    return render(
        request,
        "employee_assignments.html",
        {"employee": employee, "assignments": assignments},
    )


from django.contrib import messages


@login_required
def delete_photo(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)

    if request.method == "POST":
        job_id = photo.job.id
        photo.delete()
        messages.success(request, "Photo deleted successfully")
        return redirect("job_details", job_id=job_id)

    return render(request, "delete_photo_confirm.html", {"photo": photo})
