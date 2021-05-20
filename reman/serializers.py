from rest_framework import serializers

from reman.models import Batch, EcuModel, Repair

REPAIR_COLUMN_LIST = [
    'identify_number', 'batch__batch_number', 'batch__ecu_ref_base__ecu_type__technical_data',
    'batch__ecu_ref_base__ecu_type__supplier_oe', 'batch__ecu_ref_base__ecu_type__hw_reference', 'psa_barcode',
    'status', 'quality_control', 'closing_date', 'modified_by__username', 'modified_at', 'created_by__username',
    'created_at'
]

ECU_REF_BASE_COLUMN_LIST = [
    'ecu_type__ecu_ref_base__reman_reference', 'ecu_type__technical_data', 'ecu_type__hw_reference',
    'ecu_type__supplier_oe', 'psa_barcode', 'ecu_type__spare_part__code_produit',
    'ecu_type__spare_part__code_emplacement', 'ecu_type__spare_part__cumul_dispo'
]


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
    modified_by = serializers.CharField(source='modified_by.username', read_only=True, default='')
    created_by = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Repair
        fields = (
            'id', 'identify_number', 'batch', 'technical_data', 'supplier_oe', 'hw_reference', 'psa_barcode', 'status',
            'quality_control', 'checkout', 'closing_date', 'modified_by', 'modified_at', 'created_by', 'created_at'
        )


class EcuRefBaseSerializer(serializers.ModelSerializer):
    reman_reference = serializers.CharField(source='ecu_type.ecu_ref_base.reman_reference', read_only=True, default="")
    technical_data = serializers.CharField(source='ecu_type.technical_data', read_only=True, default="")
    hw_reference = serializers.CharField(source='ecu_type.hw_reference', read_only=True, default="")
    supplier_oe = serializers.CharField(source='ecu_type.supplier_oe', read_only=True, default="")
    code_produit = serializers.CharField(source='ecu_type.spare_part.code_produit', read_only=True, default="")
    code_emplacement = serializers.CharField(source='ecu_type.spare_part.code_emplacement', read_only=True, default="")
    cumul_dispo = serializers.CharField(source='ecu_type.spare_part.cumul_dispo', read_only=True, default="")

    class Meta:
        model = EcuModel
        fields = (
            'id', 'reman_reference', 'technical_data', 'hw_reference', 'supplier_oe', 'psa_barcode', 'code_produit',
            'code_emplacement', 'cumul_dispo'
        )
