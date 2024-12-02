from django import forms
from .models import Post, Comment

class PostCreateForm(forms.ModelForm):
    
    class Meta:
        model = Post
        fields = ("title", "text", "status", "cover", "category")
        labels = {
            'title' : 'عنوان',
            'text' : 'متن',
            'status' : 'وضعیت',
            'cover' : 'عکس',
            'category' : 'دسته بندی',
        }
        
class CommentForm(forms.ModelForm):
    
    class Meta :
        model = Comment
        fields = ('text', )
        labels = {
            'text' : 'نظر شما'
        }