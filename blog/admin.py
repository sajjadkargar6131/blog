from django.contrib import admin
from taggit.managers import TaggableManager
from django.utils.text import slugify
from . import models
import re


def clean_slug(title):
    title = re.sub(r'[^\w\s-]', '', title)
    title = re.sub(r'[-\s]+', '-', title)
    title = title.strip('-')
    if not title:
        title = 'پست'
    return title


class AdminComment(admin.ModelAdmin):
    list_display = ['user', 'post', 'text', 'datetime_created', 'publish']


class AdminPost(admin.ModelAdmin):
    formfield_overrides = {
        TaggableManager: {'help_text': 'برچسب ها را با فاصله از هم جدا کنید.'}
    }
    prepopulated_fields = {"slug": ("title",)}

    def save_model(self, request, obj, form, change):
        if not obj.slug or 'title' in form.changed_data:
            base_slug = slugify(clean_slug(obj.title), allow_unicode=True)
            unique_slug = base_slug
            if models.Post.objects.filter(slug=unique_slug).exclude(pk=obj.pk).exclude(pk=obj.pk).exists():
                unique_slug = f'{base_slug}-{obj.pk or "temp"}'
            obj.slug = unique_slug
        super().save_model(request, obj, form, change)


admin.site.register(models.Post, AdminPost)

admin.site.register(models.Comment, AdminComment)

admin.site.register(models.Like)

admin.site.register(models.Category)
