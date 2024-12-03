from django.urls import path
from . import views
urlpatterns = [
    
    path('create/', views.PostCreateView.as_view(), name='post_create'),
    
    path('', views.IndexListView.as_view(), name='blog_index'),
    
    path('<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    
    path('<slug:slug>/update/', views.PostUpdateView.as_view(), name='post_update'),
    
    path('<slug:slug>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    
    path('bookmark/<int:post_id>/', views.bookmark_post, name='bookmark_post'),
]
