import operator
from functools import reduce
from model_utils import Choices
from django.db.models import Q

from squalaetp.models import Xelon, Corvet

XELON_COLUMN_LIST = [
    'numero_de_dossier', 'vin', 'modele_produit', 'modele_vehicule', 'date_retour', 'type_de_cloture', 'nom_technicien'
]

CORVET_COLUMN_LIST = [
    'vin', 'electronique_14f', 'electronique_94f', 'electronique_14x', 'electronique_94x', 'electronique_14a',
    'electronique_94a', 'electronique_14b', 'electronique_94b'
]

# ORDER_XELON_COLUMN_CHOICES = Choices(
#     *[(str(i), elt, elt) for i, elt in enumerate(XELON_COLUMN_LIST, start=2)]
# )
#
# ORDER_CORVET_COLUMN_CHOICES = Choices(
#     *[(str(i), elt, elt) for i, elt in enumerate(CORVET_COLUMN_LIST, start=1)]
# )


class QueryTableByArgs:

    def __init__(self, queryset, column_list, column_start, **kwargs):
        self.queryset = queryset
        self.columns = column_list
        self.choices = self._choices(column_list, column_start)
        self.draw = int(kwargs.get('draw', None)[0])
        self.length = int(kwargs.get('length', None)[0])
        self.start = int(kwargs.get('start', None)[0])
        self.order_column = kwargs.get('order[0][column]', None)[0]
        self.total = queryset.count()

        search_value = kwargs.get('search[value]', None)[0]
        order = kwargs.get('order[0][dir]', None)[0]

        self._ordering(order)
        self._filter(search_value)

    def values(self):
        count = self.queryset.count()
        queryset = self.queryset.order_by(self.order_column)[self.start:self.start + self.length]
        return {
            'items': queryset,
            'count': count,
            'total': self.total,
            'draw': self.draw
        }

    def _filter(self, search_value):
        if search_value:
            object_q = [Q((col + "__icontains", search_value)) for col in self.columns]
            self.queryset = self.queryset.filter(reduce(operator.or_, object_q))

    def _ordering(self, order):
        self.order_column = self.choices[self.order_column]
        # django orm '-' -> desc
        if order == 'desc':
            self.order_column = '-' + self.order_column

    @staticmethod
    def _choices(column_list, column_start):
        return Choices(
            *[(str(i), elt, elt) for i, elt in enumerate(column_list, start=column_start)]
        )


# def query_table_by_args(filter, queryset, order_choices, **kwargs):
#     draw = int(kwargs.get('draw', None)[0])
#     length = int(kwargs.get('length', None)[0])
#     start = int(kwargs.get('start', None)[0])
#     search_value = kwargs.get('search[value]', None)[0]
#     order_column = kwargs.get('order[0][column]', None)[0]
#     order = kwargs.get('order[0][dir]', None)[0]
#
#     order_column = order_choices[order_column]
#     # django orm '-' -> desc
#     if order == 'desc':
#         order_column = '-' + order_column
#
#     total = queryset.count()
#
#     if search_value:
#         queryset = filter(queryset, search_value)
#
#     count = queryset.count()
#     queryset = queryset.order_by(order_column)[start:start + length]
#     return {
#         'items': queryset,
#         'count': count,
#         'total': total,
#         'draw': draw
#     }
#
#
# def xelon_filter(queryset, search_value):
#     object_q = [Q((col + "__icontains", search_value)) for col in XELON_COLUMN_LIST]
#     queryset = queryset.filter(reduce(operator.or_, object_q))
#     return queryset
#
#
# def corvet_filter(queryset, search_value):
#     object_q = [Q((col + "__icontains", search_value)) for col in CORVET_COLUMN_LIST]
#     queryset = queryset.filter(reduce(operator.or_, object_q))
#     return queryset
