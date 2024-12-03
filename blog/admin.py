from django.contrib import admin
from . import models
from taggit.managers import TaggableManager

class AdminComment(admin.ModelAdmin):
    list_display =['user', 'post', 'text', 'datetime_created']
    
class AdminPost(admin.ModelAdmin):
    formfield_overrides = {
        TaggableManager : {'help_text' : 'برچسب ها را با فاصله از هم جدا کنید.'}
    } 
admin.site.register(models.Post, AdminPost)

admin.site.register(models.Comment, AdminComment)

admin.site.register(models.Like)

admin.site.register(models.Category)