from django.db import models


class SiteSetting(models.Model):
    site_name = models.CharField(max_length=50, verbose_name='نام سایت', blank=True)
    site_title = models.CharField(max_length=50, verbose_name='title سایت', blank=True)
    site_title_seo = models.CharField(max_length=50, verbose_name='seo title', blank=True)
    site_description = models.TextField(verbose_name='توضیحات سئوی سایت', blank=True)
    footer_text = models.CharField(max_length=255, verbose_name='متن فوتر', blank=True)
    about_text = models.TextField(verbose_name='درباره وبلاگ', blank=True)
    show_about_text = show_top_post = models.BooleanField(verbose_name='نمایش درباره وبلاگ در صفحه اصلی', default=True)
    show_social_links = models.BooleanField(verbose_name="نمایش لینک‌های اجتماعی در صفحه اصلی", default=True)
    show_top_post = models.BooleanField(verbose_name='نمایش پست های برتر در صفحه اصلی', default=True)
    show_random_post = models.BooleanField(verbose_name='نمایش رندوم پست ها', default=True)
    show_recent_post = models.BooleanField(verbose_name='نمایش پست های اخیر', default=True)
    show_tags = models.BooleanField(verbose_name='نمایش تگ ها', default=True)
    show_categories = models.BooleanField(verbose_name='نمایش دسته بندی ها', default=True)
    show_monthly_archive = models.BooleanField(verbose_name='نمایش آرشیو ماهانه', default=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    class Meta:
        verbose_name = 'تنظیمات سایت'
        verbose_name_plural = "تنظیمات سایت"

    def __str__(self):
        return "تنظیمات سایت"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class SocialLink(models.Model):
    name = models.CharField(max_length=50, verbose_name="نام شبکه اجتماعی")
    url = models.URLField(verbose_name="لینک")
    icon_class = models.CharField(max_length=50, verbose_name="کلاس آیکون (اختیاری)", blank=True)

    class Meta:
        verbose_name = "لینک اجتماعی"
        verbose_name_plural = "لینک‌های اجتماعی"

    def __str__(self):
        return self.name
