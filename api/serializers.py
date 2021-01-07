from django.contrib.auth.models import User, Group
from rest_framework import serializers

from squalaetp.models import Xelon
from raspeedi.models import Raspeedi, UnlockProduct
from reman.models import Batch, EcuModel, Repair
from psa.models import Corvet


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

    class Meta:
        model = Corvet
        fields = ('vin', 'rad_ref', 'rad_cal', 'nav_ref', 'nav_cal',
                  'cmm_ref', 'cmm_cal', 'bsi_ref', 'bsi_cal')


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


class UnlockUpdateSerializer(UnlockSerializer):
    class Meta:
        model = UnlockProduct
        fields = UnlockSerializer.Meta.fields + ('active',)


class RemanBatchSerializer(serializers.ModelSerializer):
    reman_reference = serializers.CharField(source='ecu_ref_base.reman_reference', read_only=True)
    ecu_type = serializers.CharField(source='ecu_ref_base.ecu_type.technical_data')
    hw_reference = serializers.CharField(source='ecu_ref_base.ecu_type.hw_reference', read_only=True)
    supplier = serializers.CharField(source='ecu_ref_base.ecu_type.supplier_oe', read_only=True)
    created_by = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Batch
        fields = (
            'batch_number', 'quantity', 'reman_reference', 'ecu_type', 'hw_reference', 'supplier', 'start_date',
            'end_date', 'active', 'created_by', 'created_at'
        )


class RemanCheckOutSerializer(serializers.ModelSerializer):
    reman_reference = serializers.CharField(source='ecu_type.ecu_ref_base.reman_reference', read_only=True)
    ecu_type = serializers.CharField(source='ecu_type.technical_data')
    hw_reference = serializers.CharField(source='ecu_type.hw_reference', read_only=True)
    supplier = serializers.CharField(source='ecu_type.supplier_oe', read_only=True)
    ref_cal_out = serializers.CharField(source='ecu_type.ecu_ref_base.ref_cal_out', read_only=True)
    ref_psa_out = serializers.CharField(source='ecu_type.ecu_ref_base.ref_psa_out', read_only=True)
    open_diag = serializers.CharField(source='ecu_type.ecu_ref_base.open_diag', read_only=True)
    ref_mat = serializers.CharField(source='ecu_type.ecu_ref_base.ref_mat', read_only=True)
    ref_comp = serializers.CharField(source='ecu_type.ecu_ref_base.ref_comp', read_only=True)
    cal_ktag = serializers.CharField(source='ecu_type.ecu_ref_base.cal_ktag', read_only=True)
    status = serializers.CharField(source='ecu_type.ecu_ref_base.status', read_only=True)

    class Meta:
        model = EcuModel
        fields = (
            'psa_barcode', 'reman_reference', 'ecu_type', 'hw_reference', 'supplier', 'ref_cal_out', 'ref_psa_out',
            'open_diag', 'ref_mat', 'ref_comp', 'cal_ktag', 'status'
        )


class RemanRepairSerializer(serializers.ModelSerializer):
    batch = serializers.CharField(source='batch.batch_number', read_only=True)
    technical_data = serializers.CharField(source='batch.ecu_ref_base.ecu_type.technical_data', read_only=True)
    supplier_oe = serializers.CharField(source='batch.ecu_ref_base.ecu_type.supplier_oe', read_only=True)
    hw_reference = serializers.CharField(source='batch.ecu_ref_base.ecu_type.hw_reference', read_only=True)
    created_by = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Repair
        fields = (
            'identify_number', 'batch', 'technical_data', 'supplier_oe', 'hw_reference', 'psa_barcode', 'status',
            'quality_control', 'closing_date', 'modified_by', 'modified_at', 'created_by', 'created_at'
        )
