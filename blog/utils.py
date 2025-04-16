import re
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from PIL import Image
import os
import uuid
from datetime import date
from .models import Post


def get_clinet_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def clean_slug(title):
    title = re.sub(r'[^\w\s-]', '', title)
    title = re.sub(r'[-\s]+', '-', title)
    title = title.strip('-')
    if not title:
        title = 'پست'
    return title


def generate_unique_slug(title, instance=None):
    base_slug = slugify(clean_slug(title), allow_unicode=True)
    unique_slug = base_slug

    if instance is None or not instance.pk:
        # برای پست جدید
        if Post.objects.filter(slug=unique_slug).exists():
            instance_temp = Post(title=title)  # برای گرفتن pk بعد از save اولیه
            instance_temp.save()
            unique_slug = f'{base_slug}-{instance_temp.pk}'
            instance_temp.delete()  # حذفش می‌کنیم چون فقط برای گرفتن pk بود
    else:
        # برای پست آپدیت شده
        if Post.objects.filter(slug=unique_slug).exclude(pk=instance.pk).exists():
            unique_slug = f'{base_slug}-{instance.pk}'

    return unique_slug


ALLOWED_FORMATS = ['JPEG', 'PNG', 'WEBP']
MAX_SIZE = 10 * 1024 * 1024
MAX_WIDTH = 600
MAX_HEIGHT = 400


@csrf_exempt
def custom_upload_function(request):
    if request.method == 'POST' and request.FILES.get('upload'):
        upload = request.FILES['upload']

        # بررسی حجم فایل
        if upload.size > MAX_SIZE:
            return JsonResponse({'error': 'حجم فایل نباید بیشتر از 10 مگابایت باشد.'}, status=400)

        try:
            img = Image.open(upload)
            if img.format not in ALLOWED_FORMATS:
                return JsonResponse({'error': 'فرمت تصویر پشتیبانی نمی‌شود.'}, status=400)

            # ساخت مسیر ذخیره با تاریخ امروز
            today_str = date.today().isoformat()  # مثل: 2025-04-14
            folder_path = os.path.join(settings.MEDIA_ROOT, 'uploads', today_str)
            os.makedirs(folder_path, exist_ok=True)

            # نام یکتا برای فایل
            file_ext = os.path.splitext(upload.name)[-1]
            filename = f"{uuid.uuid4().hex}{file_ext}"
            file_path = os.path.join(folder_path, filename)

            # تغییر سایز و ذخیره
            img.thumbnail((MAX_WIDTH, MAX_HEIGHT))
            img.save(file_path)

            file_url = f"{settings.MEDIA_URL}uploads/{today_str}/{filename}"
            return JsonResponse({'url': file_url})

        except Exception as e:
            return JsonResponse({'error': f'خطا در پردازش تصویر: {e}'}, status=500)

    return JsonResponse({'error': 'درخواست نامعتبر.'}, status=400)
