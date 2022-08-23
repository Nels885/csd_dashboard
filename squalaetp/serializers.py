from rest_framework import serializers

from .models import Xelon, XelonTemporary, Sivin, SparePart

XELON_COLUMN_LIST = [
    'numero_de_dossier', 'vin', 'modele_produit', 'product__category', 'modele_vehicule', 'date_retour',
    'type_de_cloture', 'date_expedition_attendue', 'nom_technicien'
]

XELON_TEMP_COLUMN_LIST = [
    'numero_de_dossier', 'vin', 'modele_produit', 'modele_vehicule', 'is_active', 'end_date', 'created_at',
    'created_by__username'
]

SIVIN_COLUMN_LIST = [
    'immat_siv', 'codif_vin', 'marque', 'modele', 'genre_v', 'nb_portes', 'nb_pl_ass', 'version', 'energie'
]


SPAREPART_COLUMN_LIST = [
    'code_produit__name', 'code_zone', 'code_emplacement', 'cumul_dispo', 'code_magasin', 'code_site'
]


class XelonSerializer(serializers.ModelSerializer):
    activity = serializers.CharField(source='product.get_category_display', read_only=True, default='')

    class Meta:
        model = Xelon
        fields = (
            'id', 'numero_de_dossier', 'vin', 'modele_produit', 'activity', 'modele_vehicule', 'date_retour',
            'type_de_cloture', 'date_expedition_attendue', 'nom_technicien', 'vin_error'
        )


class SivinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sivin
        fields = (
            'immat_siv', 'codif_vin', 'marque', 'modele', 'genre_v', 'nb_portes', 'nb_pl_ass', 'version', 'energie'
        )


class SparePartSerializer(serializers.ModelSerializer):
    product_code = serializers.CharField(source='code_produit.name', read_only=True, default='')

    class Meta:
        model = SparePart
        fields = (
            'product_code', 'code_zone', 'code_emplacement', 'cumul_dispo', 'code_magasin', 'code_site'
        )


class XelonTemporarySerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = XelonTemporary
        fields = (
            'id', 'numero_de_dossier', 'vin', 'modele_produit', 'modele_vehicule', 'is_active', 'end_date',
            'created_at', 'created_by'
        )
