from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget

from news.models import News


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
