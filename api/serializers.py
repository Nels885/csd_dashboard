from rest_framework import serializers

from squalaetp.models import Xelon
from tools.models import ThermalChamberMeasure, BgaTime, RaspiTime


class ProgSerializer(serializers.ModelSerializer):
    """
    Serializer for the programming data that will be used by the Raspeedi tool
    """
    xelon = serializers.CharField(source='numero_de_dossier', read_only=True)
    xelon_model = serializers.CharField(source='modele_produit', read_only=True)
    xelon_vehicle = serializers.CharField(source='modele_vehicule', read_only=True)
    hw_ref = serializers.CharField(source='corvet.electronique_14x', read_only=True)
    cal = serializers.CharField(source='corvet.electronique_94x', read_only=True)
    product = serializers.CharField(source='corvet.prods.btel.name', read_only=True)
    level = serializers.CharField(source='corvet.prods.btel.level', read_only=True)
    type = serializers.CharField(source='corvet.prods.btel.type', read_only=True)

    class Meta:
        model = Xelon
        fields = (
            'xelon', 'vin', 'xelon_model', 'xelon_vehicle', 'hw_ref', 'cal', 'product', 'level', 'type'
        )


class CalSerializer(serializers.ModelSerializer):
    """
    Serializer of the calibration data that will be used by the calibration tool
    """
    rad_ref = serializers.CharField(source='corvet.electronique_14f')
    rad_cal = serializers.CharField(source='corvet.electronique_94f')
    radio_name = serializers.CharField(source='corvet.prods.radio.xelon_name', read_only=True, default="")
    nav_ref = serializers.CharField(source='corvet.electronique_14x')
    nav_cal = serializers.CharField(source='corvet.electronique_94x')
    btel_name = serializers.CharField(source='corvet.prods.btel.xelon_name', read_only=True, default="")
    cmm_ref = serializers.CharField(source='corvet.electronique_14a')
    cmm_cal = serializers.CharField(source='corvet.electronique_94a')
    cmm_name = serializers.CharField(source='corvet.prods.cmm.xelon_name', read_only=True, default="")
    bsi_ref = serializers.CharField(source='corvet.electronique_14b')
    bsi_cal = serializers.CharField(source='corvet.electronique_94b')
    bsi_name = serializers.CharField(source='corvet.prods.bsi.xelon_name', read_only=True, default="")

    class Meta:
        model = Xelon
        fields = (
            'numero_de_dossier', 'vin', 'modele_produit', 'modele_vehicule', 'rad_ref', 'rad_cal', 'radio_name',
            'nav_ref', 'nav_cal', 'btel_name', 'cmm_ref', 'cmm_cal', 'cmm_name', 'bsi_ref', 'bsi_cal', 'bsi_name'
        )


class ThermalChamberMeasureSerializer(serializers.ModelSerializer):

    class Meta:
        model = ThermalChamberMeasure
        fields = "__all__"


class ThermalChamberMeasureCreateSerializer(ThermalChamberMeasureSerializer):

    class Meta:
        model = ThermalChamberMeasure
        fields = ('value',)


class BgaTimeSerializer(serializers.ModelSerializer):

    class Meta:
        model = BgaTime
        fields = "__all__"


class BgaTimeCreateSerializer(BgaTimeSerializer):

    class Meta:
        model = BgaTime
        fields = ('name',)


class RaspiTimeSerializer(serializers.ModelSerializer):

    class Meta:
        model = RaspiTime
        fields = "__all__"


class RaspiTimeCreateSerializer(RaspiTimeSerializer):

    class Meta:
        model = RaspiTime
        fields = ('name', 'type', 'xelon')
