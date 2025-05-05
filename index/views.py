import random

from django.shortcuts import render
from django.db.models import Count
from django.db.models.functions import Substr

from blog import models
from blog.models import Post, Category
from taggit.models import Tag


def index(request):
    top_post = Post.objects.annotate(view_count=Count('views')).order_by('-view_count').first()

    monthly_archive = (
        Post.objects
            .annotate(shamsi_month=Substr('shamsi_date', 1, 7))  # "1404-02"
            .values('shamsi_month')
            .annotate(post_count=Count('id'))
            .order_by('-shamsi_month')
    )

    tags = Tag.objects.annotate(post_count=Count('taggit_taggeditem_items')).filter(post_count__gt=0)

    recent_posts = Post.objects.all().order_by('-created_at')[:5]

    categories = Category.objects.annotate(post_count=Count('posts'))

    ids = Post.objects.values_list('id', flat=True)
    random_ids = random.sample(list(ids), min(len(ids), 3))  # حداکثر ۳ پست
    random_posts = Post.objects.filter(id__in=random_ids)

    return render(request, 'index/index.html',
                  {'top_post': top_post,
                   'monthly_archive': monthly_archive,
                   'tags': tags,
                   'recent_posts': recent_posts,
                   'categories': categories,
                   'random_posts': random_posts,
                   }
                  )
