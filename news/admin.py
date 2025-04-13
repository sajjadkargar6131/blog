from django.contrib import admin
from .models import News, NewsComment


class AdminNews(admin.ModelAdmin):
    list_display = ['author', 'title', 'text', 'created_at', 'status']


class AdminNewsComment(admin.ModelAdmin):
    list_display = ['user', 'news', 'text', 'datetime_created', 'publish']


admin.site.register(News, AdminNews)
admin.site.register(NewsComment, AdminNewsComment)