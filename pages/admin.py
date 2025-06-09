from django.contrib import admin
from .models import StaticPage
from django.utils.text import slugify
import re


def clean_slug(title):
    title = re.sub(r'[^\w\s-]', '', title)
    title = re.sub(r'[-\s]+', '-', title)
    title = title.strip('-')
    if not title:
        title = 'صفحه'
    return title


class StaticPageAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'show_in_menu']
    fields = ['title', 'slug', 'content', 'show_in_menu']
    prepopulated_fields = {"slug": ("title",)}  # اختیاری چون خودمون می‌سازیم اسلاگ رو

    def save_model(self, request, obj, form, change):
        if not obj.slug or 'title' in form.changed_data:
            base_slug = slugify(clean_slug(obj.title), allow_unicode=True)
            unique_slug = base_slug
            qs = StaticPage.objects.filter(slug=unique_slug)
            if obj.pk:
                qs = qs.exclude(pk=obj.pk)
            if qs.exists():
                unique_slug = f'{base_slug}-{obj.pk or "temp"}'
            obj.slug = unique_slug
        super().save_model(request, obj, form, change)


admin.site.register(StaticPage, StaticPageAdmin)
