import uuid
import os
from PIL import Image, ExifTags


def get_unique_profile_path(instance, filename):
    ext = filename.split('.')[-1]
    # ساختن اسم فایل یونیک با UUID
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('accounts/profile/', filename)


def fix_image_orientation(img):
    try:
        exif = img._getexif()
        if exif is not None:
            orientation_key = next(
                key for key, val in ExifTags.TAGS.items() if val == 'Orientation'
            )
            orientation = exif.get(orientation_key)
            if orientation == 3:
                img = img.rotate(180, expand=True)
            elif orientation == 6:
                img = img.rotate(270, expand=True)
            elif orientation == 8:
                img = img.rotate(90, expand=True)
    except Exception:
        pass
    return img
