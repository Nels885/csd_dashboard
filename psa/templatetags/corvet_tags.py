from django import template

from psa.models import CorvetChoices

register = template.Library()


@register.filter(name='get_corvet')
def get_corvet(value, arg):
    """Removes all values of arg from the given string"""
    try:
        data = CorvetChoices.objects.get(key=value, column=arg)
        return data.value
    except CorvetChoices.DoesNotExist:
        return f"* {value} *"
