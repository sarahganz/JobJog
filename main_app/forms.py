from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    UserChangeForm,
)
from .models import Job, Employee, STATUSES, CustomUser, Employer


class JobAssignmentForm(forms.ModelForm):
    employee = forms.ModelChoiceField(queryset=Employee.objects.all())
    status = forms.ChoiceField(choices=STATUSES)

    class Meta:
        model = Job
        fields = ["employee", "status"]


class EmployeeRegistrationForm(UserCreationForm):
    skills = forms.CharField(max_length=100)
    hourly_rate = forms.DecimalField(max_digits=10, decimal_places=2)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "password1",
            "password2",
            "hourly_rate",
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        skills = self.cleaned_data.get("skills")
        hourly_rate = self.cleaned_data.get("hourly_rate")

        if commit:
            user.save()

        return user


class InviteEmployeeForm(forms.Form):
    employee_email = forms.EmailField(label="Employee Email", max_length=254)



class EmployerRegistrationForm(UserCreationForm):
    company_name = forms.CharField(max_length=100)

    class Meta(UserCreationForm.Meta):
        model = CustomUser

        fields = [
            "username",
            "first_name",
            "last_name",
            "company_name",
            "email",
            "phone_number",
            "password1",
            "password2",
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()

        return user


class EmployerLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(EmployerLoginForm, self).__init__(*args, **kwargs)
        self.fields["username"].label = "Email"
        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Enter your email"}
        )
        self.fields["password"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Enter your password"}
        )


class EmployeeLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(EmployeeLoginForm, self).__init__(*args, **kwargs)
        self.fields["username"].label = "Email"
        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Enter your email"}
        )
        self.fields["password"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Enter your password"}
        )


class AssignEmployeeForm(forms.Form):
    employees = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
        label="Select Employees",
    )

    def __init__(self, *args, employees=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["employees"].queryset = employees
        self.fields[
            "employees"
        ].label_from_instance = lambda obj: obj.user.get_full_name()
