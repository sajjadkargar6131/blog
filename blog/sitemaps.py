from django.contrib.sitemaps import Sitemap
from .models import Post


class PublishedPostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Post.objects.filter(status='pub')

    def lastmod(self, obj):
        return obj.modified_at

    def location(self, obj):
        return obj.get_absolute_url()
