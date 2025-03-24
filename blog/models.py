from django.db import models
from django.shortcuts import reverse
from django.contrib.auth import get_user_model
from taggit.managers import TaggableManager


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Post(models.Model):
    CHOICES = [
        ['pub', 'Published'],
        ['drf', 'Draft']
    ]
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField()
    status = models.CharField(choices=CHOICES, max_length=3)
    cover = models.ImageField(upload_to='covers/', blank=True)
    categories = models.ManyToManyField(Category, related_name='posts', blank=True)
    tags = TaggableManager(blank=True)
    slug = models.SlugField(unique=True, max_length=200, allow_unicode=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"slug": self.slug})


class Comment(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    text = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    publish = models.BooleanField(default=False)
    datetime_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.user} : {self.text}'


class Like(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    datetime_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Like by {self.user} on {self.post.title}'


class BookmarkPost(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='bookmarks')
    datetime_saved = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'Post {self.post} saved by {self.user}'


class PostView(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='views')
    ip_address = models.GenericIPAddressField()
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True)
    datetime_viewed = models.DateTimeField(auto_now_add=True)
