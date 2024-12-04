from django.db import models
from django.shortcuts import reverse
from django.contrib.auth import get_user_model
from taggit.managers import TaggableManager
from django.utils.text import slugify
import re

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
    slug = models.SlugField(unique=True, max_length=200, allow_unicode =True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"slug": self.slug})
    
    def clean_slug(title) :
        title = re.sub(r'[^\w\s-]', '', title)
        title = re.sub(r'[-\s]+', '-', title)
        title = title.strip('-')
        if not title :
            title = 'default-slug'
        return title
    
    # def save(self, *args, **kwargs) :
    #     if not self.pk :
    #         super().save(*args, **kwargs)
    #     if not self.slug :
    #         base_slug = slugify(self.clean_slug(self.title), allow_unicode=True)
    #         self.slug = f'{base_slug}--{self.pk}'
    #         super().save(*args, **kwargs)    
    
class Comment(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete = models.CASCADE)
    text = models.TextField()
    post = models.ForeignKey(Post, on_delete = models.CASCADE, related_name='comments')
    datetime_created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return f'{self.user} : {self.text}'


class Like(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    datetime_created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Like by {self.user} on {self.post.title}'
    
    

class BookmarkPost(models.Model) :
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='bookmarks')
    datetime_saved = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return f'Post {self.post} saved by {self.user}'
