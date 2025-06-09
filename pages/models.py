from django.db import models
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field

from blog.utils import generate_unique_slug


class StaticPage(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200, allow_unicode=True, blank=True)
    content = CKEditor5Field(config_name='extends')
    show_in_menu = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self.title, instance=self)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('page_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title
