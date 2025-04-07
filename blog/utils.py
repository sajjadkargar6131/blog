import re
from django.utils.text import slugify
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
