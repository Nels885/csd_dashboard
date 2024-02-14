import os
from django import template
from django.utils.translation import gettext as _

register = template.Library()


@register.filter(name='range')
def filter_range(start, end):
    return range(start, end)


@register.filter(name='boolean')
def boolean(value):
    if isinstance(value, bool) and value is True:
        return _('Yes')
    if value.isdigit() and int(value) == 1:
        return _('Yes')
    return _('No')


@register.filter
def filename(value):
    try:
        return os.path.basename(value.name)
    except AttributeError:
        return value
