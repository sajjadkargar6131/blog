from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('profile/picture/delete/', views.delete_profile_picture, name='delete_profile_picture'),
]
