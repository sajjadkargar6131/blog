from django import template

register = template.Library()


@register.filter
def format_number(value):
    try:
        if value >= 1000 and value < 1000000:
            value = value / 1000
            return f'{value:.1f}K'
        if value >= 1000000 and value < 1000000000:
            value = value / 1000000
            return f'{value:.1f}M'
        return value
    except (ValueError, TypeError):
        return value
