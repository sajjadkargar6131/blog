from django import forms
from .models import Post, Category, Comment
from taggit.forms import TagField


class CustomTagfield(TagField):
    def clean(self, value):
        return [t.strip() for t in value.split() if t.strip()]


class PostCreateForm(forms.ModelForm):
    tags = CustomTagfield()
    tags = TagField(
        help_text="برچسب ها را با فاصله از هم جدا کنید.",
        label="تگ ها",
        required=False,
    )
    new_category = forms.CharField(
        max_length=100,
        required=False,
        label='ایجاد دسته بندی جدید'
    )

    class Meta:
        model = Post
        fields = ("title", "text", "status", "cover", "categories", "tags", "meta_description")
        labels = {
            'title': 'عنوان',
            'text': 'متن',
            'status': 'وضعیت',
            'cover': 'عکس',
            'categories': 'دسته بندی ها'
        }
        widgets = {
            'categories': forms.CheckboxSelectMultiple,
            'meta_description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        is_create = kwargs.pop('is_create', False)
        super().__init__(*args, **kwargs)
        if not is_create:
            self.fields.pop('new_category')

    def save(self, commit=True):

        # ذخیره پست بدون تغییرات در categories
        post_instance = super().save(commit=False)

        # ذخیره پست قبل از هر چیز
        post_instance.save()

        # افزودن دسته بندی جدید در صورتی که مشخص شده باشد
        new_category_name = self.cleaned_data.get('new_category')
        if new_category_name:
            category, created = Category.objects.get_or_create(name=new_category_name)
            post_instance.categories.add(category)  # افزودن دسته بندی جدید

        # افزودن دسته بندی های انتخابی
        categories = self.cleaned_data.get('categories')
        if categories:
            post_instance.categories.set(categories)  # تنظیم دسته بندی ها (حذف گزینه های قبلی و افزودن جدید)

        return post_instance


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'نظر شما'
        }
