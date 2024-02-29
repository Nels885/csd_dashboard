from rest_framework import serializers

from utils.django.api_rest.serializers import DynamicFieldsModelSerializer
from .models import Corvet, DefaultCode, Multimedia, Ecu

CORVET_COLUMN_LIST = [
    'vin', 'electronique_14f', 'electronique_94f', 'prods__radio__xelon_name', 'electronique_14x', 'electronique_94x',
    'prods__btel__xelon_name', 'electronique_14a', 'electronique_94a', 'prods__cmm__xelon_name', 'electronique_14b',
    'electronique_94b', 'prods__bsi__xelon_name'
]

DTC_COLUMN_LIST = [
    'code', 'type', 'description', 'characterization', 'location', 'ecu_type'
]


class CorvetSerializer(DynamicFieldsModelSerializer):
    """
    Serializer for the Corvet table with conversion of column names
    """
    rad_ref = serializers.CharField(source='electronique_14f')
    rad_cal = serializers.CharField(source='electronique_94f')
    radio_name = serializers.CharField(source='prods.radio.xelon_name', read_only=True, default="")
    nav_ref = serializers.CharField(source='electronique_14x')
    nav_cal = serializers.CharField(source='electronique_94x')
    btel_name = serializers.CharField(source='prods.btel.xelon_name', read_only=True, default="")
    cmm_ref = serializers.CharField(source='electronique_14a')
    cmm_cal = serializers.CharField(source='electronique_94a')
    cmm_name = serializers.CharField(source='prods.cmm.xelon_name', read_only=True, default="")
    bsi_ref = serializers.CharField(source='electronique_14b')
    bsi_cal = serializers.CharField(source='electronique_94b')
    bsi_name = serializers.CharField(source='prods.bsi.xelon_name', read_only=True, default="")

    class Meta:
        model = Corvet
        fields = ('vin', 'rad_ref', 'rad_cal', 'radio_name', 'nav_ref', 'nav_cal', 'btel_name',
                  'cmm_ref', 'cmm_cal', 'cmm_name', 'bsi_ref', 'bsi_cal', 'bsi_name', )


class DefaultCodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = DefaultCode
        fields = ('code', 'type', 'description', 'characterization', 'ecu_type')


class DTCServerSideSerializer(serializers.ModelSerializer):

    class Meta:
        model = DefaultCode
        fields = ('code', 'type', 'description', 'characterization', 'location', 'ecu_type')


class MultimediaSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='get_name_display', read_only=True)

    class Meta:
        model = Multimedia
        fields = ('comp_ref', 'label_ref', 'name')


class EcuSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ecu
        fields = ('comp_ref', 'label_ref', 'name')
