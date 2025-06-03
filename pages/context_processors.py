from .models import StaticPage


def menu_pages(request):
    pages = StaticPage.objects.filter(show_in_menu=True)
    return {'menu_pages': pages}
