from django.contrib import admin
from .models import News, NewsComment
from .forms import NewsCreateForm


class AdminNews(admin.ModelAdmin):
    list_display = ['author', 'title', 'text', 'created_at', 'status']
    form = NewsCreateForm
    def save_model(self, request, obj, form, change):
        if not change:  # فقط هنگام ایجاد
            obj.author = request.user
        obj.save()


class AdminNewsComment(admin.ModelAdmin):
    list_display = ['user', 'news', 'text', 'datetime_created', 'publish']


admin.site.register(News, AdminNews)
admin.site.register(NewsComment, AdminNewsComment)