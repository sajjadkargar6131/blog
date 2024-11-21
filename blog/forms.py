from django import forms
from .models import Post

class PostCreateForm(forms.ModelForm):
    
    class Meta:
        model = Post
        fields = ("author", "title", "text", "status", "cover")
        labels = {
            'author' : 'نویسنده',
            'title' : 'عنوان',
            'text' : 'متن',
            'status' : 'وضعیت',
            'cover' : 'عکس'
        }