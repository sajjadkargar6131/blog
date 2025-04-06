from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords
from django.urls import reverse
from .models import News


class LatestNewsFeeds(Feed):
    title = 'آخرین اخبار'
    link = '/news/rss/'
    description = 'آخرین اخبار منتشره'

    def items(self):
        return News.objects.filter(status='pub').order_by('-created_at')[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return truncatewords(item.text, 30)

    def item_link(self, item):
        return item.get_absolute_url()

