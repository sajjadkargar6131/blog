from django.shortcuts import render
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy


def profile(request):
    return render(request, 'accounts/profile.html')
