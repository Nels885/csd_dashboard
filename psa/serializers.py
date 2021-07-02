from rest_framework import serializers

from utils.django.api_rest.serializers import DynamicFieldsModelSerializer
from .models import Corvet

CORVET_COLUMN_LIST = [
    'vin', 'electronique_14f', 'electronique_94f', 'prods__radio__name', 'electronique_14x', 'electronique_94x',
    'prods__btel__name', 'electronique_14a', 'electronique_94a', 'electronique_14b', 'electronique_94b'
]


class CorvetSerializer(DynamicFieldsModelSerializer):
    """
    Serializer for the Corvet table with conversion of column names
    """
    rad_ref = serializers.CharField(source='electronique_14f')
    rad_cal = serializers.CharField(source='electronique_94f')
    radio_name = serializers.CharField(source='prods.radio.get_name_display', read_only=True, default="")
    nav_ref = serializers.CharField(source='electronique_14x')
    nav_cal = serializers.CharField(source='electronique_94x')
    btel_name = serializers.CharField(source='prods.btel.get_name_display', read_only=True, default="")
    cmm_ref = serializers.CharField(source='electronique_14a')
    cmm_cal = serializers.CharField(source='electronique_94a')
    bsi_ref = serializers.CharField(source='electronique_14b')
    bsi_cal = serializers.CharField(source='electronique_94b')

    class Meta:
        model = Corvet
        fields = ('vin', 'rad_ref', 'rad_cal', 'radio_name', 'nav_ref', 'nav_cal', 'btel_name',
                  'cmm_ref', 'cmm_cal', 'bsi_ref', 'bsi_cal')
