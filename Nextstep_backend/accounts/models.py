from django.db import models
from django.contrib.auth.models import AbstractUser

from django.conf import settings

# Create your models here.
class User(AbstractUser):
    # Define the choices for the role field
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('graduate', 'Graduate'),
        ('professional', 'Professional'),
    )
    email = models.EmailField(unique=True)
    # Use the choices argument in the CharField
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='student',  # You can set a default value if you want
        blank=True,
        null=True
    )
    
    bio = models.TextField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username


class UserToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="token")
    access_token = models.TextField(blank=True, null=True)
    refresh_token = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Token for {self.user.username}"