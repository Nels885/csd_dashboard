import operator
from functools import reduce
from model_utils import Choices
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.viewsets import ModelViewSet


class QueryTableByArgs:

    def __init__(self, queryset, column_list, column_start, **kwargs):
        self.queryset = queryset
        self.columns = column_list
        self.choices = self._choices(column_list, column_start)
        self.draw = int(kwargs.get('draw', '')[0])
        self.length = int(kwargs.get('length', '')[0])
        self.start = int(kwargs.get('start', '')[0])
        self.order_column = kwargs.get('order[0][column]', '')[0]
        self.total = queryset.count()

        search_value = kwargs.get('search[value]', '')[0]
        order = kwargs.get('order[0][dir]', '')[0]

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


class ServerSideViewSet(ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    column_list = []
    column_start = 0

    def list(self, request, **kwargs):
        try:
            self._filter(request)
            query = QueryTableByArgs(self.queryset, self.column_list, self.column_start, **request.query_params).values()
            serializer = self.serializer_class(query["items"], many=True)
            data = {
                "data": serializer.data,
                "draw": query["draw"],
                "recordsTotal": query["total"],
                "recordsFiltered": query["count"],
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as err:
            return Response(err, status=status.HTTP_404_NOT_FOUND)

    def _filter(self, request):
        pass
