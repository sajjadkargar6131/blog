from io import BytesIO
from uuid import uuid4

from PIL import Image
from django import forms
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from django_ckeditor_5.widgets import CKEditor5Widget
from accounts.utils import fix_image_orientation
from django.db.models.fields.files import FieldFile
from django.core.files.uploadedfile import UploadedFile
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

        # اگر cover یک FieldFile (فایلِ موجود روی مدل) است:
        # یعنی کاربر فایل جدید آپلود نکرده — نیازی به اعتبارسنجی نداریم.
        if isinstance(cover, FieldFile):
            return cover

        # الان cover باید یک UploadedFile (فایل جدید) باشد — اعتبارسنجی کنیم.
        max_size = 5 * 1024 * 1024  # 5MB
        if cover.size > max_size:
            raise ValidationError("حجم تصویر نباید بیشتر از ۵ مگابایت باشد.")

        # سعی کن فایل را باز کنی و با Pillow معتبر بودنش را چک کنی.
        try:
            cover.open()
        except Exception:
            # ممکن است قبلاً باز باشد یا storage خاصی داشته باشد؛ بی‌خیال و ادامه بده
            pass

        try:
            # verify() فقط صحت فرمت را چک می‌کند؛ بعد از verify باید pointer را برگردانیم
            with Image.open(cover) as img:
                img.verify()
                fmt = img.format  # نگه می‌داریم تا بعداً بررسی کنیم
        except UnidentifiedImageError:
            raise ValidationError("فایل تصویر معتبر نیست یا خراب است.")
        except Exception:
            raise ValidationError("خطا در خواندن فایل تصویر.")
        finally:
            # بعد از verify حتماً pointer را به ابتدای فایل برگردان
            try:
                cover.seek(0)
            except Exception:
                pass

        # اگر تمایل داری فقط JPEG/PNG را قبول کنی، WEBP را از لیست حذف کن.
        allowed = {"JPEG", "JPG", "PNG", "WEBP"}
        if (fmt or "").upper() not in allowed:
            raise ValidationError("فرمت تصویر باید JPEG یا PNG باشد.")

        return cover

    def save(self, commit=True):
        instance = super().save(commit=False)

        cover = self.cleaned_data.get('cover')

        # اگر کاربر فایل جدید آپلود کرده (UploadedFile)، آن را به WEBP تبدیل کن.
        if cover and isinstance(cover, UploadedFile):
            try:
                cover.open()
            except Exception:
                pass

            try:
                img = Image.open(cover)
            except UnidentifiedImageError:
                # بهتر است این خطا اصولاً در clean_cover گرفته شده باشد؛ اینجا فقط محافظه‌کارانه
                raise ValidationError("فایل تصویر معتبر نیست یا خراب است.")

            # اصلاح جهت‌گیری اگر تابع شما اینکار را انجام می‌دهد
            img = fix_image_orientation(img)

            # مطمئن شو تصویر در حالت RGB است
            if img.mode != "RGB":
                img = img.convert("RGB")

            output = BytesIO()
            img.save(output, format='WEBP', quality=80)
            img.close()
            output.seek(0)

            filename = f"{uuid4().hex}-converted_news_cover.webp"
            webp_image = InMemoryUploadedFile(
                output,
                field_name='cover',  # ست کن به اسم فیلد واقعی
                name=filename,
                content_type='image/webp',
                size=output.getbuffer().nbytes,
                charset=None
            )
            instance.cover = webp_image
        # اگر cover یک FieldFile (فایل قبلی) هست یا None، کاری نکنیم — فایل قبلی حفظ می‌شود.

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
