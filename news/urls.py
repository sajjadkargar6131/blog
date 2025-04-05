from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.NewsCreateView.as_view(), name='news_create'),
    path('', views.NewsListView.as_view(), name='news_list'),
    path('detail/<int:pk>', views.NewsDetailView.as_view(), name='news_detail'),
]
