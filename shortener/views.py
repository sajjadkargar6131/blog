from django.shortcuts import get_object_or_404, redirect
from .models import ShortLink


def redirect_short_link(request, code):
    short_link = get_object_or_404(ShortLink, short_code=code)
    return redirect(short_link.original_url)
