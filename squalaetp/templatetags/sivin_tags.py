from django import template
from django.core.exceptions import FieldDoesNotExist

from squalaetp.models import Sivin

register = template.Library()


@register.filter(name='get_sivin_name')
def get_sivin_name(field_name):
    """
    Returns verbose_name for a field.
    """
    try:
        return Sivin._meta.get_field(field_name).verbose_name
    except FieldDoesNotExist:
        return "!!! FIELD NOT FOUND !!!"
