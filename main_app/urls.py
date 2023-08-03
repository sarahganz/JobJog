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
    path("employer/logout/", views.employer_logout, name="employer_logout"),
    path("employer/dashboard/", views.employer_dashboard, name="employer_dashboard"),
    path("invite_employee/", views.invite_employee, name="invite_employee"),
    path(
        "employee/registration/<str:invite_token>/",
        views.employee_registration,
        name="employee_registration",
    ),
    path("employee/clock-in/", views.clock_in, name="clock_in"),
    path("employee/clock-out/", views.clock_out, name="clock_out"),
    path("job/assignment/", views.job_assignment, name="job_assignment"),
    path("clock_in/<int:assignment_id>/", views.clock_in, name="clock_in"),
    path("clock_out/<int:assignment_id>/", views.clock_out, name="clock_out"),
    path("job/<int:job_id>/", views.job_details, name="job_details"),
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("jobs/", views.jobs_index, name="index"),
    path("jobs/<int:job_id>/", views.jobs_detail, name="detail"),
    path("jobs/create/", views.JobCreate.as_view(), name="jobs_create"),
    path("jobs/<int:pk>/update/", views.JobUpdate.as_view(), name="jobs_update"),
    path("jobs/<int:pk>/delete/", views.JobDelete.as_view(), name="jobs_delete"),
]
