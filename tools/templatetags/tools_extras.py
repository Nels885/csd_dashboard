from django import template
from django.utils import timezone

from tools.models import ThermalChamber

register = template.Library()


@register.filter(name='past_time')
def past_time(obj):
    """Removes all values of arg from the given string"""
    try:
        therm = ThermalChamber.objects.get(id=obj.id)
        if therm.start_time:
            delta = timezone.now() - therm.start_time
            return str(delta).split('.')[0]
        else:
            return "---"
    except (ThermalChamber.DoesNotExist, AttributeError):
        return "---"


@register.filter(name='usage_time')
def usage_time(obj):
    try:
        therm = ThermalChamber.objects.get(id=obj.id)
        if therm.start_time and therm.stop_time:
            delta = therm.stop_time - therm.start_time
            return str(delta).split('.')[0]
        else:
            return "---"
    except (ThermalChamber.DoesNotExist, AttributeError):
        return "---"


@register.filter(name='suptech_msg')
def suptech_msg(value):
    try:
        data_dict = eval(value)
        if isinstance(data_dict, dict):
            return data_dict.get('msg')
    except Exception:
        pass
    return value


@register.filter(name='suptech_type')
def suptech_type(value):
    try:
        data_dict = eval(value)
        if isinstance(data_dict, dict):
            return f"{data_dict.get('type').capitalize()}:"
    except Exception:
        pass
    return "Message:"
