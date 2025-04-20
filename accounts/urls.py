from django.urls import path
from . import views
from .views import CustomPasswordChangeView

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('profile/picture/delete/', views.delete_profile_picture, name='delete_profile_picture'),
    path("jj/change/", CustomPasswordChangeView.as_view(), name="account_change"),
]
