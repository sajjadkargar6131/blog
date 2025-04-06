from django.db import models
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field


class News(models.Model):
    CHOICES = [
        ['pub', 'Published'],
        ['drf', 'Draft']
    ]
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = CKEditor5Field(config_name='extends')
    status = models.CharField(choices=CHOICES, max_length=3)
    cover = models.ImageField(upload_to='news/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'خبر'
        verbose_name_plural = 'خبرها'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('news_detail', kwargs={'pk': self.pk})
