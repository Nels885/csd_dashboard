from django.contrib.auth.models import User, Group
from rest_framework import serializers

from psa.serializers import CorvetSerializer
from squalaetp.models import Xelon
from raspeedi.models import Raspeedi, UnlockProduct


class UserSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:user-detail")
    groups = serializers.HyperlinkedIdentityField(view_name="api:group-detail")

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:user-detail")

    class Meta:
        model = Group
        fields = ('url', 'name')


class RaspeediSerializer(serializers.ModelSerializer):
    """
    Serializer for the Raspeedi table
    """

    class Meta:
        model = Raspeedi
        fields = ('ref_boitier', 'produit', 'facade', 'dump_peedi', 'media', 'dump_renesas',)


class ProgSerializer(serializers.ModelSerializer):
    """
    Serializer for the programming data that will be used by the Raspeedi tool
    """
    corvet = CorvetSerializer(read_only=True, fields=(
        'rad_ref', 'rad_cal', 'nav_ref', 'nav_cal', 'cmm_ref', 'cmm_cal', 'bsi_ref', 'bsi_cal'
    ))

    class Meta:
        model = Xelon
        fields = ('numero_de_dossier', 'vin', 'modele_produit', 'modele_vehicule', 'corvet')


class CalSerializer(serializers.ModelSerializer):
    """
    Serializer of the calibration data that will be used by the calibration tool
    """
    corvet = CorvetSerializer(read_only=True, fields=('rad_ref', 'rad_cal', 'nav_ref', 'nav_cal'))

    class Meta:
        model = Xelon
        fields = ('numero_de_dossier', 'vin', 'modele_produit', 'modele_vehicule', 'corvet')


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
