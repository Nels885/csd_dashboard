from rest_framework import serializers

from .models import ToolStatus, UnlockProduct, Raspeedi, Log


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
        fields = ('id', 'name', 'comment', 'url')


class ToolLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = Log
        fields = ('id', 'content', 'added_at', 'content_type', 'object_id')
