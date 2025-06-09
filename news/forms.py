from io import BytesIO
from PIL import Image
from django import forms
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from django_ckeditor_5.widgets import CKEditor5Widget
from accounts.utils import fix_image_orientation
from news.models import News, NewsComment

class NewsCreateForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ("title", "text", "status", "cover",)
        labels = {
            'title': 'عنوان',
            'text': 'متن خبر',
            'status': 'وضعیت',
            'cover': 'عکس',
        }
        widgets = {
            "text": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, config_name="extends"
            )
        }

    def clean_cover(self):
        cover = self.cleaned_data.get('cover')
        if not cover:
            return cover

        max_size = 5 * 1024 * 1024  # 5MB
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
        instance = super().save(commit=False)

        cover = self.cleaned_data.get('cover')
        if cover:
            cover.open()
            img = Image.open(cover)
            img = fix_image_orientation(img)
            img = img.convert('RGB')

            output = BytesIO()
            img.save(output, format='WEBP', quality=80)
            output.seek(0)

            webp_image = InMemoryUploadedFile(
                output,
                field_name='ImageField',
                name='converted_news_cover.webp',
                content_type='image/webp',
                size=output.getbuffer().nbytes,
                charset=None
            )
            instance.cover = webp_image

        if commit:
            instance.save()

        return instance

class NewsCommentForm(forms.ModelForm):
    class Meta:
        model = NewsComment
        fields = ('text',)
        labels = {
            'text': 'نظر شما'
        }
