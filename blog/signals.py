import os
import re
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from django.conf import settings
from .models import Post


@receiver(pre_delete, sender=Post)
def delete_ckeditor_images_on_post_delete(sender, instance, **kwargs):
    # استخراج مسیر عکس‌ها از فیلد CKEditor
    pattern = rf'src="(?:{re.escape(settings.MEDIA_URL)}|/media/)(uploads/\d{{4}}-\d{{2}}-\d{{2}}/[^"]+)"'
    image_paths = re.findall(pattern, instance.text)

    # نگه‌داشتن پوشه‌هایی که بررسی می‌کنیم بعداً حذف بشن
    checked_folders = set()

    for relative_path in image_paths:
        full_path = os.path.join(settings.MEDIA_ROOT, relative_path)
        folder_path = os.path.dirname(full_path)
        checked_folders.add(folder_path)

        if os.path.exists(full_path):
            try:
                os.remove(full_path)
            except Exception as e:
                print(f" خطا در حذف تصویر: {e}")

    # حذف پوشه‌هایی که خالی شدن
    for folder in checked_folders:
        if os.path.exists(folder) and not os.listdir(folder):
            try:
                os.rmdir(folder)
            except Exception as e:
                print(f" خطا در حذف پوشه خالی: {e}")


@receiver(pre_save, sender=Post)
def delete_old_cover_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return  # پست جدیده، چیزی برای حذف وجود نداره

    try:
        old_instance = Post.objects.get(pk=instance.pk)
    except Post.DoesNotExist:
        return

    old_cover = old_instance.cover
    new_cover = instance.cover

    if old_cover and old_cover != new_cover:
        old_cover_path = os.path.join(settings.MEDIA_ROOT, old_cover.name)
        if os.path.exists(old_cover_path):
            os.remove(old_cover_path)