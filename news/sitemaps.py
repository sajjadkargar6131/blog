from django.contrib.sitemaps import Sitemap
from .models import News


class PublishedNewsSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return News.objects.filter(status='pub')

    def lastmod(self, obj):
        return obj.modified_at

    def location(self, obj):
        return obj.get_absolute_url()
