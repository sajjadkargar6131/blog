from django.contrib import admin
from .models import News


class AdminNews(admin.ModelAdmin):
    list_display = ['author', 'title', 'text', 'created_at', 'status']


admin.site.register(News, AdminNews)
