import random

from django.shortcuts import render
from django.db.models import Count, Q
from django.db.models.functions import Substr

from blog.models import Post, Category
from taggit.models import Tag


def index(request):
    top_post = Post.objects.annotate(view_count=Count('views')).filter(status='pub').order_by('-view_count').first()

    monthly_archive = (
        Post.objects
            .filter(status='pub')
            .annotate(shamsi_month=Substr('shamsi_date', 1, 7))  # "1404-02"
            .values('shamsi_month')
            .annotate(post_count=Count('id'))
            .order_by('-shamsi_month')
    )

    published_post_ids = Post.objects.filter(status='pub').values_list('id', flat=True)

    tags = Tag.objects.annotate(
        post_count=Count('taggit_taggeditem_items', filter=Q(
            taggit_taggeditem_items__object_id__in=published_post_ids
        ))
    ).filter(post_count__gt=0)

    recent_posts = Post.objects.filter(status='pub').order_by('-created_at')[:5]

    categories = Category.objects.annotate(
        post_count=Count('posts', filter=Q(posts__status='pub'))
    ).filter(post_count__gt=0)

    ids = Post.objects.values_list('id', flat=True)
    random_ids = random.sample(list(ids), min(len(ids), 3))  # حداکثر ۳ پست
    random_posts = Post.objects.filter(id__in=random_ids, status='pub')

    return render(request, 'index/index.html',
                  {'top_post': top_post,
                   'monthly_archive': monthly_archive,
                   'tags': tags,
                   'recent_posts': recent_posts,
                   'categories': categories,
                   'random_posts': random_posts,
                   }
                  )
