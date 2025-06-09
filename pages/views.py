from django.views.generic import DetailView
from .models import StaticPage


class StaticPageDetailView(DetailView):
    model = StaticPage
    template_name = 'pages/static_page_detail.html'
    context_object_name = 'page'
    slug_url_kwarg = 'slug'
