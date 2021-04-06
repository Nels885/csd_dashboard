from rest_framework import serializers

from .models import Xelon

XELON_COLUMN_LIST = [
    'numero_de_dossier', 'vin', 'modele_produit', 'modele_vehicule', 'date_retour', 'type_de_cloture', 'nom_technicien'
]


class XelonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Xelon
        fields = (
            'id', 'numero_de_dossier', 'vin', 'modele_produit', 'modele_vehicule', 'date_retour', 'type_de_cloture',
            'nom_technicien', 'corvet'
        )
