from django.db import models
from django.contrib.auth.models import AbstractUser
from .utils import get_unique_profile_path
from config import settings


class CustomUser(AbstractUser):
    profile_picture = models.ImageField(upload_to=get_unique_profile_path, null=True, blank=True, )


class Activity(models.Model):
    ACTION_CHOICES = [
        ('login', 'ورود به حساب کاربری'),
        ('logout', 'خروج از حساب کاربری'),
        ('profile_edit', 'ویرایش پروفایل'),
        ('post_create', 'ارسال پست جدید'),
        ('comment_create', 'ارسال دیدگاه'),
        ('post_edit', 'ویرایش پست '),
        ('post_delete', 'حذف پست '),
        ('news_create', 'ارسال خبر جدید'),
        ('news_edit', 'ویرایش خبر '),
        ('news_delete', 'حذف خبر '),

    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()}"

    def get_icon(self):
        icons = {
            'login': 'fa-sign-in text-success',
            'logout': 'fa-sign-out  text-danger',
            'profile_edit': 'fa-edit text-primary',
            'post_create': 'fa-file text-info',
            'comment_create': 'fa-comment text-warning',
            'post_edit': 'fa-pencil text-primary',
            'post_delete': 'fa-trash text-danger',
            'news_create': 'fa-rss-square text-info',
            'news_edit': 'fa-edit text-primary',
            'news_delete': 'fa-trash text-danger',

        }
        return icons.get(self.action, 'fa-info-circle')
