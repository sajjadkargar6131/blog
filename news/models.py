
from django.db import models
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field

from config import settings


class News(models.Model):
    CHOICES = [
        ['pub', 'Published'],
        ['drf', 'Draft']
    ]
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = CKEditor5Field(config_name='extends')
    status = models.CharField(choices=CHOICES, max_length=3)
    cover = models.ImageField(upload_to='news/cover/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'خبر'
        verbose_name_plural = 'خبرها'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('news_detail', kwargs={'pk': self.pk})

    @property
    def comments_count(self):
        return self.comments.filter(publish=True).count()

class NewsComment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='comments')
    publish = models.BooleanField(default=False)
    datetime_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'کامنت'
        verbose_name_plural = 'کامنت ها'

    def __str__(self):
        return f'{self.user} : {self.text}'

