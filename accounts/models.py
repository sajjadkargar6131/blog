from django.db import models
from django.contrib.auth.models import AbstractUser
from .utils import get_unique_profile_path


class CustomUser(AbstractUser):
    profile_picture = models.ImageField(upload_to=get_unique_profile_path, null=True, blank=True, )
