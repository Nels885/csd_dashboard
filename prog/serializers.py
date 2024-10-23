from rest_framework import serializers

from .models import ToolStatus, UnlockProduct, Raspeedi, Log, AETMeasure


class RaspeediSerializer(serializers.ModelSerializer):
    """
    Serializer for the Raspeedi table
    """
    hw_ref = serializers.CharField(source='ref_boitier', read_only=True)
    product = serializers.CharField(source='produit', read_only=True)
    level = serializers.CharField(source='facade', read_only=True)

    class Meta:
        model = Raspeedi
        fields = ('hw_ref', 'product', 'level', 'type', 'dump_peedi', 'media', 'dump_renesas',)


class UnlockSerializer(serializers.ModelSerializer):
    xelon = serializers.CharField(source='unlock.numero_de_dossier', read_only=True)
    vin = serializers.CharField(source='unlock.vin', read_only=True)

    class Meta:
        model = UnlockProduct
        fields = ('id', 'xelon', 'vin')


class UnlockUpdateSerializer(UnlockSerializer):
    class Meta:
        model = UnlockProduct
        fields = UnlockSerializer.Meta.fields + ('active',)


class ToolStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = ToolStatus
        fields = ('id', 'name', 'hostname', 'comment', 'url')


class ToolStatusUpdateSerializer(ToolStatusSerializer):

    class Meta:
        model = ToolStatus
        fields = ('last_boot', 'ip_addr', 'mac_addr', 'hw_revision', 'firmware', 'fw_version')


class ToolLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = Log
        fields = ('id', 'content', 'added_at', 'content_type', 'object_id')


class AETMeasureSerializer(serializers.ModelSerializer):
    xelon = serializers.CharField(source='content_object.xelon', read_only=True, default='')
    comp_ref = serializers.CharField(source='content_object.comp_ref', read_only=True, default='')
    manu_ref = serializers.CharField(source='content_object.manu_ref', read_only=True, default='')
    aet_name = serializers.CharField(source='content_object.aet_name', read_only=True, default='')
    prod_name = serializers.CharField(source='content_object.prod_name', read_only=True, default='')
    date = serializers.CharField(source='content_object.date', read_only=True, default='')

    class Meta:
        model = AETMeasure
        fields = (
            'xelon', 'comp_ref', 'manu_ref', 'aet_name', 'prod_name', 'date', 'measure_name', 'measured_value',
            'min_value', 'max_value'
        )
