from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from ckeditor.fields import RichTextField

from utils.django.urls import reverse_lazy
from utils.conf import DICT_YEAR

STATUS_CHOICES = [('En cours', 'En cours'), ('Réparé', 'Réparé'), ('Rebut', 'Rebut')]
HW_TYPE_CHOICES = [('ECU', 'ECU'), ('NAV', 'NAV')]


class EcuType(models.Model):
    hw_reference = models.CharField("hardware", max_length=50, unique=True)
    hw_type = models.CharField("type HW", max_length=50, choices=HW_TYPE_CHOICES, default="ECU")
    technical_data = models.CharField("modèle produit", max_length=50)
    supplier_oe = models.CharField("fabriquant", max_length=50, blank=True)
    spare_part = models.ForeignKey("SparePart", on_delete=models.SET_NULL, null=True, blank=True)

    def part_name(self):
        return self.technical_data + " HW" + self.hw_reference

    def __str__(self):
        return "HW_{} - TYPE_{}".format(self.hw_reference, self.technical_data)


class EcuModel(models.Model):
    barcode = models.CharField("code barre PSA", max_length=50, unique=True)
    oe_raw_reference = models.CharField("référence OEM brute", max_length=50, blank=True)
    oe_reference = models.CharField("référence OEM", max_length=50, blank=True)
    former_oe_reference = models.CharField("ancienne référence OEM", max_length=50, blank=True)
    vehicle = models.CharField("vehicule", max_length=50, blank=True)
    fan = models.CharField('FAN', max_length=100, blank=True)
    rear_bolt = models.CharField('REAR BOLT', max_length=100, blank=True)
    ecu_type = models.ForeignKey("EcuType", on_delete=models.SET_NULL, null=True, blank=True)
    to_dump = models.BooleanField("à dumper", default=False)

    class Meta:
        permissions = [("check_ecumodel", "Can check ecu model")]

    @staticmethod
    def part_list(barcode):
        ecu_models = EcuModel.objects.filter(barcode__exact=barcode)
        msg_list = []
        if ecu_models:
            for ecu_model in ecu_models:
                try:
                    reman_refs = "/".join([query.reman_reference for query in ecu_model.ecu_type.ecurefbase_set.all()])
                    xelon_refs = ecu_model.ecu_type.spare_part.code_produit
                    location = ecu_model.ecu_type.spare_part.code_emplacement
                    msg_list.append(
                        f"Réf. REMAN : {reman_refs}  -  Réf. XELON : {xelon_refs}  -  EMPLACEMENT : {location}")
                except AttributeError:
                    pass
            return msg_list
        else:
            return None

    def __iter__(self):
        for field in self._meta.fields:
            yield field.verbose_name.capitalize(), field.value_to_string(self)

    def __str__(self):
        return "barcode_{}".format(self.barcode)


class EcuRefBase(models.Model):
    reman_reference = models.CharField("référence REMAN", max_length=10, unique=True)
    brand = models.CharField("Marque", max_length=50, blank=True)
    ref_cal_out = models.CharField("REF_CAL_OUT", max_length=10, blank=True)
    ref_psa_out = models.CharField("REF_PSA_OUT", max_length=10, blank=True)
    req_diag = models.CharField("REQ_DIAG", max_length=50, blank=True)
    open_diag = models.CharField("OPENDIAG", max_length=50, blank=True)
    req_ref = models.CharField("REQ_REF", max_length=50, blank=True)
    ref_mat = models.CharField("REF_MAT", max_length=10, blank=True)
    ref_comp = models.CharField("REF_COMP", max_length=10, blank=True)
    req_cal = models.CharField("REQ_CAL", max_length=50, blank=True)
    cal_ktag = models.CharField("CAL_KTAG", max_length=10, blank=True)
    req_status = models.CharField("REQ_STATUS", max_length=50, blank=True)
    status = models.CharField("STATUT", max_length=50, blank=True)
    test_clear_memory = models.CharField("TEST_CLEAR_MEMORY", max_length=10, blank=True)
    cle_appli = models.CharField("CLE_APPLI", max_length=50, blank=True)
    map_data = models.CharField("map data", max_length=100, blank=True)
    product_part = models.CharField("product part", max_length=8, blank=True)
    pf_code = models.CharField("PF code REMAN", max_length=10, blank=True)
    ecu_type = models.ForeignKey("EcuType", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.reman_reference


class Batch(models.Model):
    year = models.CharField("années", max_length=1)
    number = models.IntegerField("numéro de lot", validators=[MaxValueValidator(999), MinValueValidator(1)])
    quantity = models.IntegerField('quantité', validators=[MaxValueValidator(999), MinValueValidator(1)])
    box_quantity = models.IntegerField('quantité du carton', default=6,
                                       validators=[MaxValueValidator(6), MinValueValidator(1)])
    batch_number = models.CharField("numéro de lot", max_length=10, blank=True, unique=True)
    customer = models.CharField("client", max_length=50, default="PSA")
    active = models.BooleanField("terminé", default=True)
    is_barcode = models.BooleanField("Nouveau code barre", default=False)
    start_date = models.DateField("date de début", null=True)
    end_date = models.DateField("date de fin", null=True)
    closing_date = models.DateTimeField("date de cloture", null=True, blank=True)
    created_at = models.DateTimeField(editable=False, auto_now_add=True)
    created_by = models.ForeignKey(User, editable=False, on_delete=models.CASCADE)
    ecu_ref_base = models.ForeignKey(EcuRefBase, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        permissions = [("pdfgen_batch", "Can pdfgen batch")]

    def clean(self):
        if not self.year:
            date = timezone.now()
            if date.year in DICT_YEAR.keys():
                self.year = DICT_YEAR[date.year]
            else:
                raise ValidationError(_('Impossible formatting of the year!'))

    def __str__(self):
        return self.batch_number


class Default(models.Model):
    code = models.CharField("code defaut", max_length=30, unique=True)
    description = models.CharField("libellé", max_length=200)
    ecu_type = models.ManyToManyField("EcuType", related_name="defaults", blank=True)

    def __str__(self):
        return "{} - {}".format(self.code, self.description)


class Repair(models.Model):

    identify_number = models.CharField("n° d'identification", max_length=10, unique=True)
    barcode = models.CharField("code barre", max_length=100, blank=True)
    vin = models.CharField("V.I.N.", max_length=20, blank=True)
    diagnostic_data = models.TextField("Données Diagnostique", max_length=50000, blank=True)
    new_barcode = models.CharField("nouveau code barre", max_length=100, blank=True)
    product_number = models.CharField("référence", max_length=50, blank=True)
    remark = models.CharField("remarques", max_length=200, blank=True)
    comment = RichTextField("Commentaires action", max_length=500, config_name="comment", blank=True)
    face_plate = models.BooleanField("façade", default=False)
    metal_case = models.BooleanField("boitier", default=False)
    fan = models.BooleanField("ventilateur", default=False)
    locating_pin = models.BooleanField("Boulon arrière", default=False)
    spring_locking = models.BooleanField("verrouillage à ressort", default=False)
    status = models.CharField("status", max_length=50, default='En cours', choices=STATUS_CHOICES)
    closing_reason = models.CharField("motif de clôture", max_length=200, blank=True)
    quality_control = models.BooleanField("contrôle qualité", default=False)
    checkout = models.BooleanField("contrôle de sortie", default=False)
    closing_date = models.DateTimeField("date de cloture", null=True, blank=True)
    recovery = models.BooleanField("reprise", default=False)
    created_at = models.DateTimeField('ajouté le', editable=False, auto_now_add=True)
    created_by = models.ForeignKey(User, related_name="repairs_created", editable=False, on_delete=models.CASCADE)
    modified_at = models.DateTimeField('modifié le', auto_now=True)
    modified_by = models.ForeignKey(User, related_name="repairs_modified", on_delete=models.SET_NULL, null=True,
                                    blank=True)
    batch = models.ForeignKey(Batch, related_name="repairs", on_delete=models.CASCADE)
    default = models.ForeignKey("Default", related_name="repairs", on_delete=models.SET_NULL, null=True, blank=True)
    parts = GenericRelation('RepairPart')

    class Meta:
        ordering = ['-modified_at']
        permissions = [
            ("close_repair", "Can close repair"),
            ("stock_repair", "Can stock repair")
        ]

    def get_absolute_url(self):
        if self.pk:
            return reverse_lazy('reman:edit_repair', args=[self.pk])
        return reverse_lazy('reman:repair_table', get={'filter': 'quality'})

    @classmethod
    def search(cls, value):
        if isinstance(value, str):
            return cls.objects.filter(
                Q(identify_number__iexact=value.strip()) | Q(batch__batch_number__iexact=value.strip()))
        return None

    def __str__(self):
        return self.identify_number


class RepairPart(models.Model):
    product_code = models.CharField('code produit', max_length=100)
    quantity = models.CharField('n° de pièce', max_length=100)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['id']
        verbose_name = "Pièce réparation"

    def __str__(self):
        return f"Pièces sur {self.content_object}"


class RepairCloseReason(models.Model):
    name = models.CharField('Nom', max_length=100, unique=True)
    extra = models.BooleanField(default=False)
    is_active = models.BooleanField("Actif", default=True)
    class Meta:
        verbose_name = "Repair Close Reason"
        ordering = ['name']

    def __str__(self):
        return self.name


class SparePart(models.Model):
    code_produit = models.CharField('code Produit', max_length=100)
    code_magasin = models.CharField('code Magasin', max_length=50, blank=True)
    code_zone = models.CharField('code Zone', max_length=50, blank=True)
    code_site = models.IntegerField('code Site', null=True, blank=True)
    code_emplacement = models.CharField('code Emplacement', max_length=50, blank=True)
    cumul_dispo = models.IntegerField('cumul Dispo', null=True, blank=True)

    def __str__(self):
        return self.code_produit
