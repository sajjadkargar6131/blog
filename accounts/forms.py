import sys

from PIL import Image
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django import forms
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ValidationError
from io import BytesIO

from .models import CustomUser
from site_settings.models import SiteSetting, SocialLink
from .utils import fix_image_orientation


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = UserCreationForm.Meta.fields


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = UserChangeForm.Meta.fields


class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['profile_picture']
        widgets = {
            'profile_picture': forms.FileInput(attrs={
                'id': 'id_profile_picture',
                'style': 'display: none;',
            })
        }

    def clean_profile_picture(self):
        picture = self.cleaned_data.get('profile_picture')

        if not picture:
            return picture  # تصویر خالی

        max_size = 5 * 1024 * 1024  # 5MB
        if picture.size > max_size:
            raise ValidationError("حجم فایل نباید بیشتر از 5 مگابایت باشد.")

        # بررسی صحت و فرمت قبل از اصلاح جهت تصویر
        try:
            img = Image.open(picture)
            img.verify()
        except Exception:
            raise ValidationError("فایل تصویر معتبر نیست یا خراب است.")

        picture.seek(0)
        img = Image.open(picture)

        # بررسی فرمت قبل از اصلاح جهت
        if img.format not in ['JPEG', 'PNG']:
            raise ValidationError("فرمت تصویر فقط باید JPEG یا PNG باشد.")

        # اصلاح جهت تصویر
        img = fix_image_orientation(img)

        # تبدیل به RGB برای WebP
        img = img.convert('RGB')

        output = BytesIO()
        img.save(output, format='WEBP', quality=80)
        output.seek(0)

        webp_image = InMemoryUploadedFile(
            file=output,
            field_name='ImageField',
            name='converted_image.webp',
            content_type='image/webp',
            size=sys.getsizeof(output),
            charset=None
        )

        return webp_image


class ProfileNameForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name']
        labels = {
            'first_name': ' نام',
            'last_name': 'نام خانوادگی'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})


class SiteSettingForm(forms.ModelForm):
    class Meta:
        model = SiteSetting
        fields = '__all__'  # یا فیلدهای موردنظرت


class SocialLinkForm(forms.ModelForm):
    class Meta:
        model = SocialLink
        fields = '__all__'
        widgets = {
            'icon_class': forms.TextInput(attrs={'placeholder': 'مثال: fa fa-instagram'}),
        }
