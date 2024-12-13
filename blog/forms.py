from django import forms
from .models import Post, Category, Comment
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
    new_category = forms.CharField(
        max_length=100,
        required=False,
        label='ایجاد دسته بندی جدید'
    )
    class Meta:
        model = Post
        fields = ("title", "text", "status", "cover", "categories", "tags")
        labels = {
            'title' : 'عنوان',
            'text' : 'متن',
            'status' : 'وضعیت',
            'cover' : 'عکس',  
            'categories' : 'دسته بندی ها'
        }
        widgets={
            'categories':forms.CheckboxSelectMultiple,
        }
        
    def __init__(self, *args, **kwargs):
        is_create = kwargs.pop('is_create', False)
        super().__init__(*args, **kwargs)
        if not is_create:
            self.fields.pop('new_category')
            
    def save(self, commit=True):
        isinstance = super().save(commit=False)
        new_category_name = self.cleaned_data.get('new_category')
        if new_category_name:
            category, created = Category.objects.get_or_create(name=new_category_name)
            isinstance.save()
            isinstance.categories.add(category)
        categories = self.cleaned_data.get('categories')
        if categories:
            isinstance.categories.set(categories)
        return isinstance    
    
                    
class CommentForm(forms.ModelForm):
    
    class Meta :
        model = Comment
        fields = ('text', )
        labels = {
            'text' : 'نظر شما'
        }