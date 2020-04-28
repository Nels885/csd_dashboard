import operator
from functools import reduce
from model_utils import Choices
from django.db.models import Q

from squalaetp.models import Xelon, Corvet

XELON_COLUMN_LIST = [
    'numero_de_dossier', 'vin', 'modele_produit', 'modele_vehicule', 'date_retour', 'type_de_cloture', 'nom_technicien'
]

CORVET_COLUMN_LIST = [
    'vin', 'electronique_14f', 'electronique_94f', 'electronique_14x', 'electronique_14a', 'electronique_94a',
    'electronique_14b', 'electronique_94b'
]

ORDER_XELON_COLUMN_CHOICES = Choices(
    *[(str(i), elt, elt) for i, elt in enumerate(XELON_COLUMN_LIST, start=2)]
)

ORDER_CORVET_COLUMN_CHOICES = Choices(
    *[(str(i), elt, elt) for i, elt in enumerate(CORVET_COLUMN_LIST, start=1)]
)


def query_table_by_args(filter, queryset, order_choices, **kwargs):
    draw = int(kwargs.get('draw', None)[0])
    length = int(kwargs.get('length', None)[0])
    start = int(kwargs.get('start', None)[0])
    search_value = kwargs.get('search[value]', None)[0]
    order_column = kwargs.get('order[0][column]', None)[0]
    order = kwargs.get('order[0][dir]', None)[0]

    order_column = order_choices[order_column]
    # django orm '-' -> desc
    if order == 'desc':
        order_column = '-' + order_column

    total = queryset.count()

    if search_value:
        queryset = filter(queryset, search_value)

    count = queryset.count()
    queryset = queryset.order_by(order_column)[start:start + length]
    return {
        'items': queryset,
        'count': count,
        'total': total,
        'draw': draw
    }


def xelon_filter(queryset, search_value):
    object_q = [Q((col + "__icontains", search_value)) for col in XELON_COLUMN_LIST]
    queryset = queryset.filter(reduce(operator.or_, object_q))
    return queryset


def corvet_filter(queryset, search_value):
    object_q = [Q((col + "__icontains", search_value)) for col in CORVET_COLUMN_LIST]
    queryset = queryset.filter(reduce(operator.or_, object_q))
    return queryset
