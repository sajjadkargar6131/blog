from django.utils.text import slugify
import re


def clean_slug(title):
    title = re.sub(r'[^\w\s-]', '', title)
    title = re.sub(r'[-\s]+', '-', title)
    title = title.strip('-')
    if not title:
        title = 'خبر'
    return title


def generate_unique_slug(title, model_class, instance=None):
    base_slug = slugify(clean_slug(title), allow_unicode=True)
    unique_slug = base_slug

    if instance is None or not instance.pk:
        if model_class.objects.filter(slug=unique_slug).exists():
            unique_slug = f"{base_slug}-1"
    else:
        if model_class.objects.filter(slug=unique_slug).exclude(pk=instance.pk).exists():
            unique_slug = f"{base_slug}-{instance.pk}"

    return unique_slug
