from io import BytesIO

from PIL import Image
from django import forms
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile

from accounts.utils import fix_image_orientation
from .models import Post, Category, Comment
from taggit.forms import TagField
from django_ckeditor_5.widgets import CKEditor5Widget


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
            'text': CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, config_name="extends"
            ),
        }

    def __init__(self, *args, **kwargs):
        is_create = kwargs.pop('is_create', False)
        super().__init__(*args, **kwargs)
        if not is_create:
            self.fields.pop('new_category')

    def clean_cover(self):
        cover = self.cleaned_data.get('cover')
        if not cover:
            return cover

        max_size = 5 * 1024 * 1024
        if cover.size > max_size:
            raise ValidationError("حجم تصویر نباید بیشتر از ۵ مگابایت باشد.")

        try:
            img = Image.open(cover)
            img.verify()
        except Exception:
            raise ValidationError("فایل تصویر معتبر نیست یا خراب است.")

        cover.seek(0)
        img = Image.open(cover)
        if img.format not in ['JPEG', 'PNG']:
            raise ValidationError("فرمت تصویر باید JPEG یا PNG باشد.")

        return cover

    def save(self, commit=True):
        post_instance = super().save(commit=False)

        # پردازش عکس
        cover = self.cleaned_data.get('cover')
        if cover:
            img = Image.open(cover)
            img = fix_image_orientation(img)
            img = img.convert('RGB')

            output = BytesIO()
            img.save(output, format='WEBP', quality=80)
            output.seek(0)

            webp_image = InMemoryUploadedFile(
                output,
                field_name='ImageField',
                name='converted_cover.webp',
                content_type='image/webp',
                size=output.getbuffer().nbytes,
                charset=None
            )
            post_instance.cover = webp_image

        if commit:
            post_instance.save()

            # بعد از ذخیره، حالا m2m ها رو ست کن
            new_category_name = self.cleaned_data.get('new_category')
            if new_category_name:
                category, created = Category.objects.get_or_create(name=new_category_name)
                post_instance.categories.add(category)

            categories = self.cleaned_data.get('categories')
            if categories:
                post_instance.categories.set(categories)

            self.save_m2m()  # مطمئن شو tags و categories ثبت شدن

        return post_instance


class CommentForm(forms.ModelForm):
    parent = forms.IntegerField(widget=forms.HiddenInput(), required=False)  # فقط فیلد اضافی برای id والد
    text = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control w-100',
        'rows': 3,
    }))

    class Meta:
        model = Comment
        fields = ('text',)  # فقط فیلد متن
        labels = {
            'text': 'نظر شما'
        }
