from django.urls import path, re_path
from . import views
urlpatterns = [
    
    path('create/', views.PostCreateView.as_view(), name='post_create'),
    
    path('', views.IndexListView.as_view(), name='blog_index'),
    
    # path('<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    re_path(r'^(?P<slug>[-\w\u0600-\u06FF]+)/$', views.PostDetailView.as_view(), name='post_detail'),
    
    path('update/<str:slug>', views.PostUpdateView.as_view(), name='post_update'),
    
    path('delete/<str:slug>', views.PostDeleteView.as_view(), name='post_delete'),
    
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    
    path('bookmark/<int:post_id>/', views.bookmark_post, name='bookmark_post'),
    
    path('archives/<int:year>/<int:month>/', views.archive_month, name='archive_month'),
]
