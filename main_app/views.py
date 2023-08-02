import os
import uuid
import boto3
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Job



# Create your views here.

def home(request):
  return render(request, 'home.html')
  
def about(request):
  return render(request, 'about.html')


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

