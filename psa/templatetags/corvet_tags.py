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
        data_list = data.split("|")
        if len(arg_list) == 2:
            select_value = int(arg_list[1])
            if len(data_list) == select_value + 1:
                return data_list[select_value]
            elif arg_list[0] == "DON_MOT" and select_value == 1:
                return f"* {value} *"
            return data_list[0]
        return data
    except (CorvetChoices.DoesNotExist, IndexError):
        return f"* {value} *"
