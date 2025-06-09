import string
import random
from django.db import models


def generate_code(length=6):
    characters = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choices(characters, k=length))
        if not ShortLink.objects.filter(short_code=code).exists():
            return code


class ShortLink(models.Model):
    original_url = models.URLField()
    short_code = models.CharField(max_length=10, unique=True, default=generate_code)

    def __str__(self):
        return f"{self.short_code} -> {self.original_url}"
