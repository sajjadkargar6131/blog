from django.contrib import admin
from .models import SiteSetting, SocialLink


class OnlySuperuserAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(SiteSetting)
class SiteSettingAdmin(OnlySuperuserAdmin):
    def has_add_permission(self, request):
        # فقط اجازه افزودن می‌دهد اگر هیچ تنظیماتی ثبت نشده باشد
        return super().has_add_permission(request) and not SiteSetting.objects.exists()


@admin.register(SocialLink)
class SocialLinkAdmin(OnlySuperuserAdmin):
    list_display = ('name', 'url', 'icon_class')
