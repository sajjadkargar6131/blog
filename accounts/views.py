import os

from allauth.account.views import PasswordChangeView
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from allauth.account.forms import ChangePasswordForm
from django.urls import reverse
from django.utils.timezone import now

from .forms import ProfilePictureForm
from .models import Activity


@login_required
def profile(request):
    user = request.user
    active_tab = request.GET.get("tab", "info")
    activities = Activity.objects.filter(user=user).order_by('-timestamp')
    change_password_form = ChangePasswordForm(request.user)

    # صفحه‌بندی فعالیت‌ها
    paginator = Paginator(activities, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
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
    else:
        form = ProfilePictureForm(instance=user)

    return render(request, 'accounts/profile.html', {
        'form': form,
        'change_password_form': change_password_form,
        'active_tab': active_tab,
        'activities': page_obj,
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
