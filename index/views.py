from django.shortcuts import render
from django.db.models import Count
from blog.models import Post
from taggit.models import Tag


def index(request):
    top_post = Post.objects.annotate(view_count=Count('views')).order_by('-view_count').first()

    monthly_archive = Post.objects.dates('created_at', 'month', order='DESC')

    tags = Tag.objects.all()

    return render(request, 'index/index.html',
                  {'top_post': top_post, 'monthly_archive': monthly_archive, 'tags': tags}
                  )
