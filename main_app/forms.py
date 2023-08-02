
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Job, Employee, STATUSES, CustomUser, Employer


class JobAssignmentForm(forms.ModelForm):
    employee = forms.ModelChoiceField(queryset=Employee.objects.all())
    status = forms.ChoiceField(choices=STATUSES)

    class Meta:
        model = Job
        fields = ["employee", "status"]


class EmployeeRegistrationForm(UserCreationForm):
    skills = forms.CharField(max_length=100)
    hourly_rate = forms.IntegerField()

    class Meta(UserCreationForm.Meta):
        model = CustomUser  # Use your custom user model

    def save(self, commit=True):
        user = super().save(commit=False)
        skills = self.cleaned_data.get("skills")
        hourly_rate = self.cleaned_data.get("hourly_rate")

        if commit:
            user.save()
            Employee.objects.create(user=user, skills=skills, hourly_rate=hourly_rate)

        return user


class InviteEmployeeForm(forms.Form):
    employee_email = forms.EmailField(label="Employee Email", max_length=254)


class EmployerRegistrationForm(UserCreationForm):
    password = forms.CharField(widget=forms.PasswordInput)
    company_name = forms.CharField(max_length=100)  # Add company_name field here

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ["username", "email", "phone_number", "password"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            Employer.objects.create(
                user=user, company_name=self.cleaned_data["company_name"]
            )  # Update this line
        return user


class EmployerLoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email")  # Use email as the username field

    class Meta:
        model = CustomUser
        fields = ("username", "password")

from django.forms import ModelForm
from .models import StatusForm

