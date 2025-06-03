from django.urls import path
from . import views

urlpatterns = [
    path('s/<str:code>/', views.redirect_short_link, name='redirect_short_link'),
]
