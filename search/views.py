from django.shortcuts import render
from django.db.models import Q
from blog.models import Post, Category  # فرض بر این است که Category در blog.models است
from news.models import News

def search_view(request):
    query = request.GET.get('q', '')
    post_results = []
    news_results = []
    category_results = []

    if query:
        post_results = Post.objects.filter(
            Q(title__icontains=query) | Q(text__icontains=query),
            status='pub'
        )

        news_results = News.objects.filter(
            Q(title__icontains=query) | Q(text__icontains=query),
            status='pub'
        )

        category_results = Category.objects.filter(
            name__icontains=query
        )

    return render(request, 'search/search_results.html', {
        'query': query,
        'post_results': post_results,
        'news_results': news_results,
        'category_results': category_results,
    })
