from django.db import models
from django.contrib.auth.models import AbstractUser

from django.conf import settings

# Create your models here.
class User(AbstractUser):
    role = models.CharField(max_length=50, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)