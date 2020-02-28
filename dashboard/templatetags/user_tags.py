from django import template
from django.contrib.auth.models import Group

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    try:
        group = Group.objects.get(name=group_name)
    except Group.DoesNotExist:
        return False
    return True if group in user.groups.all() else False


@register.filter(name='has_groups')
def has_groups(user, group_name):
    try:
        groups = Group.objects.filter(name__istartswith=group_name)
        for group in groups:
            if group in user.groups.all():
                return True
    except Group.DoesNotExist:
        return False
    return False
