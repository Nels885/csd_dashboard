from model_utils import Choices
from django.db.models import Q

from squalaetp.models import Xelon, Corvet

ORDER_XELON_COLUMN_CHOICES = Choices(
    ('0', 'numero_de_dossier'),
    ('1', 'vin'),
    ('2', 'modele_produit'),
    ('3', 'modele_vehicule'),
    ('4', 'date_retour'),
    ('5', 'type_de_cloture'),
    ('6', 'nom_technicien'),
)

ORDER_CORVET_COLUMN_CHOICES = Choices(
    ('0', 'vin'),
    ('1', 'electronique_14l'),
    ('2', 'electronique_94l'),
    ('3', 'electronique_14x'),
    ('4', 'electronique_94x'),
    ('5', 'electronique_44x'),
)


def query_xelon_by_args(**kwargs):
    draw = int(kwargs.get('draw', None)[0])
    length = int(kwargs.get('length', None)[0])
    start = int(kwargs.get('start', None)[0])
    search_value = kwargs.get('search[value]', None)[0]
    order_column = kwargs.get('order[0][column]', None)[0]
    order = kwargs.get('order[0][dir]', None)[0]

    order_column = ORDER_XELON_COLUMN_CHOICES[order_column]
    # django orm '-' -> desc
    if order == 'desc':
        order_column = '-' + order_column

    queryset = Xelon.objects.all()
    total = queryset.count()

    if search_value:
        queryset = queryset.filter(Q(numero_de_dossier__icontains=search_value) |
                                   Q(vin__icontains=search_value) |
                                   Q(modele_produit__icontains=search_value) |
                                   Q(modele_vehicule__icontains=search_value) |
                                   Q(type_de_cloture__icontains=search_value) |
                                   Q(nom_technicien__icontains=search_value))

    count = queryset.count()
    queryset = queryset.order_by(order_column)[start:start + length]
    return {
        'items': queryset,
        'count': count,
        'total': total,
        'draw': draw
    }


def query_corvet_by_args(**kwargs):
    draw = int(kwargs.get('draw', None)[0])
    length = int(kwargs.get('length', None)[0])
    start = int(kwargs.get('start', None)[0])
    search_value = kwargs.get('search[value]', None)[0]
    order_column = kwargs.get('order[0][column]', None)[0]
    order = kwargs.get('order[0][dir]', None)[0]

    order_column = ORDER_CORVET_COLUMN_CHOICES[order_column]
    # django orm '-' -> desc
    if order == 'desc':
        order_column = '-' + order_column

    queryset = Corvet.objects.all()
    total = queryset.count()

    if search_value:
        queryset = queryset.filter(Q(vin__icontains=search_value) |
                                   Q(electronique_14l__icontains=search_value) |
                                   Q(electronique_94l__icontains=search_value) |
                                   Q(electronique_94x__icontains=search_value) |
                                   Q(electronique_14x__icontains=search_value) |
                                   Q(electronique_44x__icontains=search_value))

    count = queryset.count()
    queryset = queryset.order_by(order_column)[start:start + length]
    return {
        'items': queryset,
        'count': count,
        'total': total,
        'draw': draw
    }
