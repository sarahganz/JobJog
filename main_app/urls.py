from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path(
        "employer/registration/",
        views.employer_registration,
        name="employer_registration",
    ),
    path("employer/login/", views.employer_login, name="employer_login"),
    path("accounts/login/", views.employee_login, name="employee_login"),
    path("employer/logout/", views.employer_logout, name="employer_logout"),
    path("employer/dashboard/", views.employer_dashboard, name="employer_dashboard"),
    path("invite_employee/", views.invite_employee, name="invite_employee"),
    path("employees/", views.employees_index, name="employees_index"),
    path("employees/<int:employee_id>/", views.detail_employee, name="detail_employee"),
    path("employee_dashboard/", views.employee_dashboard, name="employee_dashboard"),
    path(
        "employee/registration/<str:token>/",
        views.employee_registration,
        name="employee_registration",
    ),
    path("job/assignment/", views.job_assignment, name="job_assignment"),
    path("clock_in/<int:assignment_id>/", views.clock_in, name="clock_in"),
    path("clock_out/<int:assignment_id>/", views.clock_out, name="clock_out"),
    path("job/<int:job_id>/", views.job_details, name="job_details"),
    path("jobs/", views.jobs_index, name="index"),
    path("jobs/<int:job_id>/", views.jobs_detail, name="detail"),
    path("jobs/create/", views.JobCreate.as_view(), name="jobs_create"),
    path("jobs/<int:pk>/update/", views.JobUpdate.as_view(), name="jobs_update"),
    path("jobs/<int:pk>/delete/", views.JobDelete.as_view(), name="jobs_delete"),
]
