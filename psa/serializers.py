from rest_framework import serializers

from utils.django.api_rest.serializers import DynamicFieldsModelSerializer
from .models import Corvet

CORVET_COLUMN_LIST = [
    'vin', 'electronique_14f', 'electronique_94f', 'electronique_14x', 'electronique_94x', 'electronique_14a',
    'electronique_94a', 'electronique_14b', 'electronique_94b'
]


class CorvetSerializer(DynamicFieldsModelSerializer):
    """
    Serializer for the Corvet table with conversion of column names
    """
    rad_ref = serializers.CharField(source='electronique_14f')
    rad_cal = serializers.CharField(source='electronique_94f')
    nav_ref = serializers.CharField(source='electronique_14x')
    nav_cal = serializers.CharField(source='electronique_94x')
    cmm_ref = serializers.CharField(source='electronique_14a')
    cmm_cal = serializers.CharField(source='electronique_94a')
    bsi_ref = serializers.CharField(source='electronique_14b')
    bsi_cal = serializers.CharField(source='electronique_94b')

    class Meta:
        model = Corvet
        fields = ('vin', 'rad_ref', 'rad_cal', 'nav_ref', 'nav_cal',
                  'cmm_ref', 'cmm_cal', 'bsi_ref', 'bsi_cal')
