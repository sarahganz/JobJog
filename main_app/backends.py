# main_app/backends.py
from django.contrib.auth.backends import ModelBackend
from main_app.models import CustomUser


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Check if the user exists and their email matches the provided username
            user = CustomUser.objects.get(email=username)
        except CustomUser.DoesNotExist:
            # No user with the given email found
            return None

        if user.check_password(password):
            # Password matches, return the user
            return user

        # Invalid password
        return None
