from django.contrib.auth.models import User, Group
from rest_framework import serializers

from squalaetp.models import Xelon, Corvet
from raspeedi.models import Raspeedi


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
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class RaspeediSerializer(serializers.ModelSerializer):
    class Meta:
        model = Raspeedi
        fields = ('ref_boitier', 'produit', 'facade', 'dump_peedi', 'media', 'dump_renesas',)


class CorvetSerializer(DynamicFieldsModelSerializer):
    ref_radio = serializers.CharField(source='electronique_14l')
    cal_radio = serializers.CharField(source='electronique_94l')
    ref_nav = serializers.CharField(source='electronique_14x')
    cal_nav = serializers.CharField(source='electronique_94x')
    no_serie = serializers.CharField(source='electronique_44x')
    raspeedi = RaspeediSerializer(many=True, read_only=True)

    class Meta:
        model = Corvet
        fields = ('ref_radio', 'cal_radio', 'ref_nav', 'cal_nav', 'no_serie', 'raspeedi')


class ProgSerializer(serializers.ModelSerializer):
    corvet = CorvetSerializer(many=True, read_only=True)

    class Meta:
        model = Xelon
        fields = ('numero_de_dossier', 'vin', 'modele_produit', 'modele_vehicule', 'corvet')
        depth = 1


class CalSerializer(serializers.ModelSerializer):
    corvet = CorvetSerializer(many=True, read_only=True,
                              fields=('ref_radio', 'cal_radio', 'ref_nav', 'cal_nav', 'no_serie'))

    class Meta:
        model = Xelon
        fields = ('numero_de_dossier', 'vin', 'modele_produit', 'modele_vehicule', 'corvet')
