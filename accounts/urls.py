from django.urls import path
from . import views
from .views import CustomPasswordChangeView

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('profile/picture/delete/', views.delete_profile_picture, name='delete_profile_picture'),
    path('profile/password/change/',views.CustomPasswordChangeView.as_view(), name='password_change'),
]
