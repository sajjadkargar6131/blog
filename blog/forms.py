import os
from io import BytesIO
from uuid import uuid4

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
    remove_cover = forms.BooleanField(
        required=False,
        label='حذف تصویر فعلی'
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
        if img.format not in ['JPEG', 'PNG', 'WEBP']:
            raise ValidationError("فرمت تصویر باید JPEG یا PNG باشد.")

        return cover

    def save(self, commit=True):
        post_instance = super().save(commit=False)
        cover = self.cleaned_data.get('cover')
        remove_cover = self.cleaned_data.get('remove_cover', False)

        # آپلود و پردازش تصویر جدید
        if cover:
            with Image.open(cover) as img:
                img = fix_image_orientation(img)
                img = img.convert('RGB')

                output = BytesIO()
                img.save(output, format='WEBP', quality=80)
                output.seek(0)

                filename = f"{uuid4().hex}_cover.webp"
                webp_image = InMemoryUploadedFile(
                    output,
                    field_name='ImageField',
                    name=filename,
                    content_type='image/webp',
                    size=output.getbuffer().nbytes,
                    charset=None
                )
                post_instance.cover = webp_image

        # حذف تصویر قبلی فقط اگر تصویر جدید بارگذاری شده یا remove_cover فعال است
        if post_instance.pk and (cover or remove_cover):
            try:
                old_instance = Post.objects.get(pk=post_instance.pk)
                if old_instance.cover and (remove_cover or (cover and old_instance.cover.name != post_instance.cover.name)):
                    try:
                        if os.path.isfile(old_instance.cover.path):
                            old_instance.cover.delete(save=False)
                    except (FileNotFoundError, ValueError):
                        pass
            except Post.DoesNotExist:
                pass
            except PermissionError:
                pass

        if remove_cover:
            post_instance.cover = None

        if commit:
            post_instance.save()
            self.save_m2m()

        return post_instance


class CommentForm(forms.ModelForm):
    parent = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    text = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control w-100',
        'rows': 3,
    }))

    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'نظر شما'
        }
