from django.db import models
from django.contrib.auth.models import AbstractUser
from .utils import get_unique_profile_path
from config import settings


class CustomUser(AbstractUser):
    profile_picture = models.ImageField(upload_to=get_unique_profile_path, null=True, blank=True, )


class Activity(models.Model):
    ACTION_CHOICES = [
        ('login', 'ورود به حساب کاربری'),
        ('profile_edit', 'ویرایش پروفایل'),
        ('post_create', 'ارسال پست جدید'),
        ('comment_create', 'ارسال دیدگاه'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()}"

    def get_icon(self):
        icons = {
            'login': 'fa-check-circle text-success',
            'profile_edit': 'fa-edit text-primary',
            'post_create': 'fa-file-alt text-info',
            'comment_create': 'fa-comment text-warning',
        }
        return icons.get(self.action, 'fa-info-circle')
