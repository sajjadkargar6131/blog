from django.db import models
from django.shortcuts import reverse
from django.contrib.auth import get_user_model

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
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"pk": self.pk})
    
class Comment(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete = models.CASCADE)
    text = models.TextField()
    post = models.ForeignKey(Post, on_delete = models.CASCADE, related_name='comments')
    datetime_created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return f'{self.user} : {self.text}'
