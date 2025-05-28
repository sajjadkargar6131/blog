"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from blog import utils, sitemaps as blog_sitemap
from news import sitemaps as news_sitemaps

sitemap_patterns = {
    'post': blog_sitemap.PublishedPostSitemap,
    'news': news_sitemaps.PublishedNewsSitemap,
}

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('', include('index.urls')),
                  path('blog/', include('blog.urls')),
                  path('accounts/', include('allauth.urls')),
                  path('accounts/', include('accounts.urls')),
                  path('news/', include('news.urls')),
                  path('sitemap.xml', sitemap, {'sitemaps': sitemap_patterns}, name='sitemap'),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += [
    path("ckeditor5/", include('django_ckeditor_5.urls')),
    path("upload/", utils.custom_upload_function, name="custom_upload_function"),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
