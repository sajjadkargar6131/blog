from django.contrib import admin
from . import models

class AdminComment(admin.ModelAdmin):
    list_display =['user', 'post', 'text', 'datetime_created']
    
    
admin.site.register(models.Post)

admin.site.register(models.Comment, AdminComment)

admin.site.register(models.Like)

admin.site.register(models.Category)