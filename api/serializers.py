from django.contrib.auth.models import User, Group
from rest_framework import serializers

from squalaetp.models import Xelon, Corvet
from raspeedi.models import Raspeedi


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
        fields = ('ref_boitier', 'produit', 'facade', 'type', 'dump_peedi', 'media')


class CorvetSerializer(serializers.ModelSerializer):
    raspeedi = RaspeediSerializer(many=True)

    class Meta:
        model = Corvet
        fields = ('electronique_14l', 'electronique_94l', 'electronique_14x', 'electronique_94x', 'raspeedi')


class ProgSerializer(serializers.ModelSerializer):
    corvet = CorvetSerializer(many=True, read_only=True)

    class Meta:
        model = Xelon
        fields = ('numero_de_dossier', 'vin', 'modele_produit', 'modele_vehicule', 'corvet')
