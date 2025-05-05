from django import template

register = template.Library()

@register.filter
def shamsi_month_name(value):
    MONTH_NAMES_FA = [
        'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
        'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
    ]
    try:
        month_index = int(value)
        if 1 <= month_index <= 12:
            return MONTH_NAMES_FA[month_index - 1]
        return ''
    except (ValueError, TypeError):
        return ''

