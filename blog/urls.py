from django.urls import path
from . import views
urlpatterns = [
    # path('', views.index, name='blog_index'),
    path('', views.IndexListView.as_view(), name='blog_index'),
    
    # path('<int:pk>/', views.post_detail, name='post_detail'),
    path('<int:pk>', views.PostDetailView.as_view(), name='post_detail'),
    
    # path('create/', views.post_create, name='post_create'),
    path('create/', views.PostCreateView.as_view(), name='post_create'),
    
    
    # path('<int:pk>/update', views.post_update, name='post_update'),
    path('<int:pk>/update', views.PostUpdateview.as_view(), name='post_update'),
    
    # path('<int:pk>/delete', views.post_delete, name='post_delete'),
    path('<int:pk>/delete', views.PostDeleteView.as_view(), name='post_delete'),
]
