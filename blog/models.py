from django.db import models
from django.shortcuts import reverse
from taggit.managers import TaggableManager
from django_ckeditor_5.fields import CKEditor5Field

from config import settings


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'دسته بندی'
        verbose_name_plural = 'دسته بندی ها'


class Post(models.Model):
    CHOICES = [
        ['pub', 'Published'],
        ['drf', 'Draft']
    ]
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = CKEditor5Field(config_name='extends')
    status = models.CharField(choices=CHOICES, max_length=3)
    cover = models.ImageField(upload_to='covers/', blank=True)
    categories = models.ManyToManyField(Category, related_name='posts', blank=True)
    tags = TaggableManager(blank=True)
    slug = models.SlugField(unique=True, max_length=200, allow_unicode=True)
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="توضیح کوتاه برای سئو. حداکثر 160 کاراکتر.",
        null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'پست'
        verbose_name_plural = 'پست ها'

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"slug": self.slug})

    @property
    def comments_count(self):
        return self.comments.filter(publish=True).count()

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def bookmark_count(self):
        return self.bookmarks.count()

    @property
    def unique_views(self):
        return self.views.count()


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    publish = models.BooleanField(default=False)
    datetime_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.user} : {self.text}'

    class Meta:
        verbose_name = 'کامنت'
        verbose_name_plural = 'کامنت ها'


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    datetime_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Like by {self.user} on {self.post.title}'

    class Meta:
        verbose_name = 'لایک'
        verbose_name_plural = 'لایک ها'


class BookmarkPost(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='bookmarks')
    datetime_saved = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'Post {self.post} saved by {self.user}'


class PostView(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='views')
    ip_address = models.GenericIPAddressField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    datetime_viewed = models.DateTimeField(auto_now_add=True)
