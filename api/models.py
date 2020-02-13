from model_utils import Choices
from django.db.models import Q

from squalaetp.models import Xelon, Corvet

ORDER_XELON_COLUMN_CHOICES = Choices(
    ('2', 'numero_de_dossier'),
    ('3', 'vin'),
    ('4', 'modele_produit'),
    ('5', 'modele_vehicule'),
    ('6', 'date_retour'),
    ('7', 'type_de_cloture'),
    ('8', 'nom_technicien'),
)

ORDER_CORVET_COLUMN_CHOICES = Choices(
    ('1', 'vin'),
    ('2', 'electronique_14f'),
    ('3', 'electronique_94f'),
    ('4', 'electronique_14x'),
    ('5', 'electronique_94x'),
    ('6', 'electronique_14a'),
    ('7', 'electronique_94a'),
    ('8', 'electronique_14b'),
    ('9', 'electronique_94b'),
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

    queryset = Xelon.objects.filter(date_retour__isnull=False)
    total = queryset.count()

    if search_value:
        queryset = queryset.filter(Q(numero_de_dossier__icontains=search_value) |
                                   Q(vin__icontains=search_value) |
                                   Q(modele_produit__icontains=search_value) |
                                   Q(modele_vehicule__icontains=search_value) |
                                   Q(date_retour__icontains=search_value) |
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
                                   Q(electronique_14f__icontains=search_value) |
                                   Q(electronique_94f__icontains=search_value) |
                                   Q(electronique_94x__icontains=search_value) |
                                   Q(electronique_14x__icontains=search_value) |
                                   Q(electronique_14a__icontains=search_value) |
                                   Q(electronique_14a__icontains=search_value) |
                                   Q(electronique_94a__icontains=search_value) |
                                   Q(electronique_14b__icontains=search_value) |
                                   Q(electronique_94b__icontains=search_value))

    count = queryset.count()
    queryset = queryset.order_by(order_column)[start:start + length]
    return {
        'items': queryset,
        'count': count,
        'total': total,
        'draw': draw
    }
