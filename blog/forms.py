from django import forms
from .models import Post, Comment

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
        
class CommentForm(forms.ModelForm):
    
    class Meta :
        model = Comment
        fields = ('text', )
        labels = {
            'text' : 'نظر شما'
        }