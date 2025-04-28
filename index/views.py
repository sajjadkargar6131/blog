from django.shortcuts import render
from django.db.models import Count
from blog.models import Post
from taggit.models import Tag


def index(request):
    top_post = Post.objects.annotate(view_count=Count('views')).order_by('-view_count').first()

    monthly_archive = Post.objects.dates('created_at', 'month', order='DESC')

    tags = Tag.objects.annotate(post_count=Count('taggit_taggeditem_items')).filter(post_count__gt=0)

    recent_posts = Post.objects.all().order_by('-created_at')[:5]

    return render(request, 'index/index.html',
                  {'top_post': top_post,
                   'monthly_archive': monthly_archive,
                   'tags': tags,
                   'recent_posts': recent_posts}
                  )
