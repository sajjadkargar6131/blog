from django import template
from jalali_date import datetime2jalali
from datetime import datetime

register = template.Library()


@register.filter
def persian_month_name(value):
    month_names = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 'مهر', 'آبان', 'آذر', 'دی', 'بهمن',
                   'اسفند']

    try:
        # اگر ورودی datetime یا date باشه
        if hasattr(value, 'month'):
            # اگر شیء فقط date بود (بدون زمان)، تبدیلش کن به datetime
            if isinstance(value, datetime):
                dt = value
            else:
                dt = datetime(value.year, value.month, value.day)

            # تبدیل تاریخ میلادی به شمسی
            jalali_date = datetime2jalali(dt)
            month_number = jalali_date.month
        else:
            return ''

        return month_names[month_number]
    except (ValueError, IndexError):
        return ''
