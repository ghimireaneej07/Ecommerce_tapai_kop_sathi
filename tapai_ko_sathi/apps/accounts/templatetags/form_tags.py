from django import template
from django.utils.html import format_html

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css):
    try:
        existing = field.field.widget.attrs.get('class', '')
        if existing:
            css = f"{existing} {css}"
        field.field.widget.attrs['class'] = css
        return field
    except Exception:
        return field
