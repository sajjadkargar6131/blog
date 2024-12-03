from django import forms
from .models import Post, Comment
from taggit.forms import TagField

class CustomTagfield(TagField):
    def clean(self, value):
        return [t.strip() for t in value.split() if t.strip()]
   
class PostCreateForm(forms.ModelForm):
    tags = CustomTagfield()
    tags = TagField(
        help_text= "برچسب ها را با فاصله از هم جدا کنید.",
        label = "تگ ها",
        required=False,
    )
    class Meta:
        model = Post
        fields = ("title", "text", "status", "cover", "categories", "tags")
        labels = {
            'title' : 'عنوان',
            'text' : 'متن',
            'status' : 'وضعیت',
            'cover' : 'عکس',
            'categories' : 'دسته بندی',
            
        }
        
class CommentForm(forms.ModelForm):
    
    class Meta :
        model = Comment
        fields = ('text', )
        labels = {
            'text' : 'نظر شما'
        }