import uuid
import os


def get_unique_profile_path(instance, filename):
    ext = filename.split('.')[-1]
    # ساختن اسم فایل یونیک با UUID
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('accounts/profile/', filename)
