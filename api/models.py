import operator
from functools import reduce
from model_utils import Choices
from django.db.models import Q


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
