from django.urls import path
from . import views
from .feeds import LatestNewsFeeds

urlpatterns = [
    path('', views.NewsListView.as_view(), name='news_list'),
    path('create/', views.NewsCreateView.as_view(), name='news_create'),
    path('detail/<int:pk>', views.NewsDetailView.as_view(), name='news_detail'),
    path('delete/<int:pk>', views.NewsDeleteView.as_view(), name='news_delete'),
    path('update/<int:pk>', views.NewsUpdateView.as_view(), name='news_update'),
    path('rss/', LatestNewsFeeds(), name='news_rss'),
]
