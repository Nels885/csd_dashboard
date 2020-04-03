from django.contrib.auth.models import User, Group
from rest_framework import serializers

from squalaetp.models import Xelon, Corvet
from raspeedi.models import Raspeedi, UnlockProduct


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


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

    raspeedi = RaspeediSerializer(many=True, read_only=True)

    class Meta:
        model = Corvet
        fields = ('vin', 'rad_ref', 'rad_cal', 'nav_ref', 'nav_cal',
                  'cmm_ref', 'cmm_cal', 'bsi_ref', 'bsi_cal', 'raspeedi')


class ProgSerializer(serializers.ModelSerializer):
    """
    Serializer for the programming data that will be used by the Raspeedi tool
    """
    corvet = CorvetSerializer(many=True, read_only=True)

    class Meta:
        model = Xelon
        fields = ('numero_de_dossier', 'vin', 'modele_produit', 'modele_vehicule', 'corvet')
        depth = 1


class CalSerializer(serializers.ModelSerializer):
    """
    Serializer of the calibration data that will be used by the calibration tool
    """
    corvet = CorvetSerializer(many=True, read_only=True,
                              fields=('rad_ref', 'rad_cal', 'nav_ref', 'nav_cal'))

    class Meta:
        model = Xelon
        fields = ('numero_de_dossier', 'vin', 'modele_produit', 'modele_vehicule', 'corvet')


class XelonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Xelon
        fields = (
            'id', 'numero_de_dossier', 'vin', 'modele_produit', 'modele_vehicule', 'date_retour', 'type_de_cloture',
            'nom_technicien', 'corvet'
        )


class UnlockSerializer(serializers.ModelSerializer):
    xelon = serializers.CharField(source='unlock.numero_de_dossier', read_only=True)
    vin = serializers.CharField(source='unlock.vin', read_only=True)

    class Meta:
        model = UnlockProduct
        fields = ('id', 'xelon', 'vin')
