import os
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from news.models import News

@receiver(post_delete, sender=News)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    حذف فایل عکس وقتی که نمونه News حذف می‌شود.
    """
    if instance.cover:
        if os.path.isfile(instance.cover.path):
            try:
                os.remove(instance.cover.path)
            except Exception as e:
                print(f"خطا در حذف فایل عکس بعد از حذف نمونه: {e}")


@receiver(pre_save, sender=News)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    حذف فایل عکس قبلی وقتی عکس جدید جایگزین شود.
    """
    if not instance.pk:
        return False  # اگر نمونه تازه است، کاری نکن

    try:
        old_instance = News.objects.get(pk=instance.pk)
    except News.DoesNotExist:
        return False

    old_file = old_instance.cover
    new_file = instance.cover

    if old_file and old_file != new_file:
        if os.path.isfile(old_file.path):
            try:
                os.remove(old_file.path)
            except Exception as e:
                print(f"خطا در حذف فایل عکس قبلی هنگام جایگزینی: {e}")
