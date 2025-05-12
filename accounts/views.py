import os

from allauth.account.views import PasswordChangeView
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from allauth.account.forms import ChangePasswordForm
from django.urls import reverse
from django.utils.timezone import now

from .forms import ProfilePictureForm, ProfileNameForm
from .models import Activity

from blog.models import Post, Comment


@login_required
def profile(request):
    user = request.user
    active_tab = request.GET.get("tab", "info")
    change_password_form = ChangePasswordForm(request.user)
    change_name_family_form = ProfileNameForm(instance=user)

    # دریافت فعالیت‌ها (activities)
    activities = Activity.objects.filter(user=user).order_by('-timestamp')
    activities_paginator = Paginator(activities, 10)  # صفحه‌بندی برای فعالیت‌ها
    activities_page_number = request.GET.get('page_activities')
    activities_page_obj = activities_paginator.get_page(activities_page_number)

    # دریافت ذخیره‌شده‌ها (bookmarks)
    bookmarks = Post.objects.filter(bookmarks__user=request.user).distinct()
    bookmarks_paginator = Paginator(bookmarks, 10)  # صفحه‌بندی برای ذخیره‌شده‌ها
    bookmarks_page_number = request.GET.get('page_bookmarks')
    bookmarks_page_obj = bookmarks_paginator.get_page(bookmarks_page_number)

    # دریافت کامنت‌ها (comments)
    comments = Comment.objects.filter(user=request.user)
    comments_paginator = Paginator(comments, 10)  # صفحه‌بندی برای کامنت‌ها
    comments_page_number = request.GET.get('page_comments')
    comments_page_obj = comments_paginator.get_page(comments_page_number)

    # ساخت فرم ها در صورت ارسال درخواست GET
    form = ProfilePictureForm(instance=user)
    form2 = ProfileNameForm(instance=user)

    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'update_picture':
            old_picture_path = user.profile_picture.path if user.profile_picture else None
            form = ProfilePictureForm(request.POST, request.FILES, instance=user)
            if form.is_valid():
                if 'profile_picture' in request.FILES:
                    # حذف عکس قبلی
                    if old_picture_path and os.path.exists(old_picture_path):
                        os.remove(old_picture_path)
                form.save()
                Activity.objects.create(
                    user=user,
                    action='profile_edit',
                    timestamp=now(),
                    description='ویرایش عکس  پروفایل'
                )
                messages.success(request, 'عکس پروفایل با موفقیت به روز شد.')
                return redirect('profile')
        elif form_type == 'update_name':
            name_form = ProfileNameForm(request.POST, instance=user)
            if name_form.is_valid():
                name_form.save()
                Activity.objects.create(
                    user=user,
                    action='profile_edit',
                    timestamp=now(),
                    description='ویرایش   پروفایل'
                )
                messages.success(request, 'پروفایل با موفقیت به روز شد.')
                return redirect('profile')
    return render(request, 'accounts/profile.html', {
        'form': form,
        'form2': change_name_family_form,
        'change_password_form': change_password_form,
        'active_tab': active_tab,
        'activities': activities_page_obj,
        'bookmarks': bookmarks_page_obj,
        'comments': comments_page_obj,
    })


@login_required
def delete_profile_picture(request):
    user = request.user
    if user.profile_picture:
        user.profile_picture.delete(save=False)
        user.save()
        Activity.objects.create(
            user=user,
            action='profile_edit',
            timestamp=now(),
            description='حذف عکس پروفایل'
        )
        messages.success(request, 'عکس پروفایل با موفقیت حذف شد.')
    else:
        messages.info(request, 'عکسی برای حذف وجود نداشت.')
    return redirect('profile')


class CustomPasswordChangeView(PasswordChangeView):
    template_name = "accounts/profile.html"  # هم موفق، هم ناموفق همین قالب رو نشون بده

    def get_default_success_url(self):
        return reverse("profile") + "?tab=password"

    def form_valid(self, form):
        messages.success(self.request, "رمز عبور شما با موفقیت تغییر یافت.")
        return super().form_valid(form)

    def form_invalid(self, form):
        if 'oldpassword' in form.errors:
            messages.error(self.request, 'رمز عبور فعلی اشتباه است.')
        else:
            messages.error(self.request, 'لطفاً خطاهای فرم را بررسی کنید.')
        context = self.get_context_data(form=form)
        context['active_tab'] = 'password'
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["change_password_form"] = context.get("form")  # این خط مهمه
        return context
