from django.urls import path, re_path
from .views import StaticPageDetailView

urlpatterns = [

    re_path(r'^(?P<slug>[-\w\u0600-\u06FF]+)/$', StaticPageDetailView.as_view(), name='page_detail'),
]
