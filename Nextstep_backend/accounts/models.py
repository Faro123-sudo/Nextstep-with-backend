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

    # Use the choices argument in the CharField
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='student',  # You can set a default value if you want
        blank=True,
        null=True
    )
    
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username