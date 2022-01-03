from django import template

register = template.Library()


@register.filter(name='part_count')
def part_count(obj):
    count = 0
    try:
        for product in obj.all():
            for part in product.sparepart_set.all():
                count += part.cumul_dispo
        return count
    except (obj.DoesNotExist, AttributeError, TypeError):
        return count
