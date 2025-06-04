import os

from allauth.account.views import PasswordChangeView
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from allauth.account.forms import ChangePasswordForm
from django.urls import reverse
from django.utils.timezone import now
from django.forms import modelformset_factory

from .forms import ProfilePictureForm, ProfileNameForm, SiteSettingForm, SocialLinkForm
from .models import Activity

from site_settings.models import SiteSetting, SocialLink

from blog.models import Post, Comment



def build_profile_context(user, active_tab="info", request=None):
    # فرم‌ها
    profile_picture_form = ProfilePictureForm(instance=user)
    profile_name_form = ProfileNameForm(instance=user)
    change_password_form = ChangePasswordForm(user)

    # فعالیت‌ها
    activities = Activity.objects.filter(user=user).order_by('-timestamp')
    activities_paginator = Paginator(activities, 10)
    activities_page_number = request.GET.get('page_activities') if request else None
    activities_page_obj = activities_paginator.get_page(activities_page_number)

    # بوکمارک‌ها
    bookmarks = Post.objects.filter(bookmarks__user=user).distinct()
    bookmarks_paginator = Paginator(bookmarks, 10)
    bookmarks_page_number = request.GET.get('page_bookmarks') if request else None
    bookmarks_page_obj = bookmarks_paginator.get_page(bookmarks_page_number)

    # کامنت‌ها
    comments = Comment.objects.filter(user=user)
    comments_paginator = Paginator(comments, 10)
    comments_page_number = request.GET.get('page_comments') if request else None
    comments_page_obj = comments_paginator.get_page(comments_page_number)

    return {
        "form": profile_picture_form,
        "form2": profile_name_form,
        "change_password_form": change_password_form,
        "activities": activities_page_obj,
        "bookmarks": bookmarks_page_obj,
        "comments": comments_page_obj,
        "active_tab": active_tab
    }


@login_required
def profile(request):
    user = request.user
    active_tab = request.GET.get("tab", "info")

    # Initialize forms
    change_password_form = ChangePasswordForm(user)
    change_name_family_form = ProfileNameForm(instance=user)
    form = ProfilePictureForm(instance=user)

    # Pagination
    activities = Activity.objects.filter(user=user).order_by('-timestamp')
    bookmarks = Post.objects.filter(bookmarks__user=user).distinct()
    comments = Comment.objects.filter(user=user)

    activities_page_obj = Paginator(activities, 10).get_page(request.GET.get('page_activities'))
    bookmarks_page_obj = Paginator(bookmarks, 10).get_page(request.GET.get('page_bookmarks'))
    comments_page_obj = Paginator(comments, 10).get_page(request.GET.get('page_comments'))

    # Site Settings
    site_form = None
    social_formset = None

    if user.is_superuser:
        site_setting = SiteSetting.objects.first()
        social_links = SocialLink.objects.all()
        SocialLinkFormSet = modelformset_factory(SocialLink, form=SocialLinkForm, extra=1, can_delete=True)

        if request.method == 'POST' and request.POST.get('form_type') == 'update_settings':
            site_form = SiteSettingForm(request.POST, instance=site_setting)
            social_formset = SocialLinkFormSet(request.POST, queryset=social_links)
            if site_form.is_valid() and social_formset.is_valid():
                site_form.save()
                social_formset.save()
                Activity.objects.create(user=user, action='settings_edit', timestamp=now(),
                                        description='ویرایش تنظیمات')
                messages.success(request, "تنظیمات سایت با موفقیت ذخیره شد.")
                return redirect('profile')
        else:
            # Initialize forms for GET or any POST that isn't update_settings
            site_form = SiteSettingForm(instance=site_setting)
            social_formset = SocialLinkFormSet(queryset=social_links)

    # Other form handlers
    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'update_picture':
            old_picture_path = user.profile_picture.path if user.profile_picture else None
            form = ProfilePictureForm(request.POST, request.FILES, instance=user)
            if form.is_valid():
                if 'profile_picture' in request.FILES and old_picture_path and os.path.exists(old_picture_path):
                    os.remove(old_picture_path)
                form.save()
                Activity.objects.create(user=user, action='profile_edit', timestamp=now(),
                                        description='ویرایش عکس پروفایل')
                messages.success(request, 'عکس پروفایل با موفقیت به‌روز شد.')
                return redirect('profile')

        elif form_type == 'update_name':
            change_name_family_form = ProfileNameForm(request.POST, instance=user)
            if change_name_family_form.is_valid():
                change_name_family_form.save()
                Activity.objects.create(user=user, action='profile_edit', timestamp=now(), description='ویرایش نام')
                messages.success(request, 'پروفایل با موفقیت به‌روز شد.')
                return redirect('profile')

        elif form_type == 'change_password':
            change_password_form = ChangePasswordForm(user, request.POST)
            if change_password_form.is_valid():
                change_password_form.save()
                messages.success(request, 'رمز عبور با موفقیت تغییر یافت.')
                return redirect('profile')

    return render(request, 'accounts/profile.html', {
        'form': form,
        'form2': change_name_family_form,
        'change_password_form': change_password_form,
        'active_tab': active_tab,
        'activities': activities_page_obj,
        'bookmarks': bookmarks_page_obj,
        'comments': comments_page_obj,
        'site_form': site_form,
        'social_formset': social_formset,
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


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = "accounts/profile.html"

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
        profile_context = build_profile_context(self.request.user, active_tab="password", request=self.request)

        # اضافه کردن فرم‌های تنظیمات سایت اگر کاربر سوپر یوزر باشد
        user = self.request.user
        site_form = None
        social_formset = None
        if user.is_superuser:
            site_setting = SiteSetting.objects.first()
            social_links = SocialLink.objects.all()
            SocialLinkFormSet = modelformset_factory(SocialLink, form=SocialLinkForm, extra=1, can_delete=True)
            site_form = SiteSettingForm(instance=site_setting)
            social_formset = SocialLinkFormSet(queryset=social_links)

        context.update(profile_context)
        context['change_password_form'] = self.get_form()
        context['site_form'] = site_form
        context['social_formset'] = social_formset

        return context
