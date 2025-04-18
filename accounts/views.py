import os

from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProfilePictureForm


@login_required
def profile(request):
    user = request.user
    if request.method == 'POST':
        old_picture_path = user.profile_picture.path if user.profile_picture else None
        form = ProfilePictureForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            if 'profile_picture' in request.FILES:
                # حذف عکس قبلی
                if old_picture_path and os.path.exists(old_picture_path):
                    os.remove(old_picture_path)
            form.save()
            return redirect('profile')
    else:
        form = ProfilePictureForm(instance=user)

    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def delete_profile_picture(request):
    user = request.user
    if user.profile_picture:
        user.profile_picture.delete(save=False)
        user.save()
        messages.success(request, 'عکس پروفایل با موفقیت حذف شد.')
    else:
        messages.info(request, 'عکسی برای حذف وجود نداشت.')
    return redirect('profile')
