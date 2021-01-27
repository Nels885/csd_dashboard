from django import template

from psa.models import CorvetChoices

register = template.Library()


@register.filter(name='get_corvet')
def get_corvet(value, args):
    """Removes all values of arg from the given string"""
    try:
        arg_list = args.split(" ")
        column = arg_list[0]
        data = CorvetChoices.objects.get(key=value, column=column).value
        if len(arg_list) > 1:
            data_list = data.split("|")
            select_value = int(arg_list[1])
            return data_list[select_value]
        else:
            return data
    except (CorvetChoices.DoesNotExist, IndexError):
        return f"* {value} *"
