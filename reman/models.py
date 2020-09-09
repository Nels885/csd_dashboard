from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from ckeditor.fields import RichTextField
from crum import get_current_user

from utils.django.urls import reverse_lazy
from utils.conf import DICT_YEAR

STATUS_CHOICES = [('En cours', 'En cours'), ('Réparé', 'Réparé'), ('Rebut', 'Rebut')]


class EcuType(models.Model):
    hw_reference = models.CharField("hardware", max_length=10, unique=True)
    technical_data = models.CharField("modèle produit", max_length=50, blank=True)
    supplier_oe = models.CharField("fabriquant", max_length=50, blank=True)
    spare_part = models.ForeignKey("SparePart", on_delete=models.CASCADE, null=True, blank=True)

    def part_name(self):
        return self.technical_data + " HW" + self.hw_reference

    def __str__(self):
        return "HW_{} - TYPE_{}".format(self.hw_reference, self.technical_data)


class EcuModel(models.Model):
    psa_barcode = models.CharField("code barre PSA", max_length=10, unique=True)
    oe_raw_reference = models.CharField("réference OEM brute", max_length=10, blank=True)
    oe_reference = models.CharField("référence OEM", max_length=10, blank=True)
    sw_reference = models.CharField("software", max_length=10, blank=True)
    former_oe_reference = models.CharField("ancienne référence OEM", max_length=50, blank=True)
    supplier_es = models.CharField("service après vente", max_length=50, blank=True)
    ecu_type = models.ForeignKey("EcuType", on_delete=models.CASCADE, null=True, blank=True)

    @staticmethod
    def part_list(psa_barcode):
        ecu_models = EcuModel.objects.filter(psa_barcode__exact=psa_barcode)
        msg_list = []
        if ecu_models:
            for ecu_model in ecu_models:
                reman_refs = ecu_model.ecu_type.ecu_ref_base.reman_reference
                xelon_refs = ecu_model.ecu_type.spare_part.code_produit
                location = ecu_model.ecu_type.spare_part.code_emplacement
                msg_list.append(
                    'Réf. REMAN : {}  -  Réf. XELON : {}  -  EMPLACEMENT : {}'.format(reman_refs, xelon_refs, location))
            return msg_list
        else:
            return None

    def __iter__(self):
        for field in self._meta.fields:
            yield field.verbose_name.capitalize(), field.value_to_string(self)

    def __str__(self):
        return "PSA_barcode_{}".format(self.psa_barcode)


class EcuRefBase(models.Model):
    reman_reference = models.CharField("référence REMAN", max_length=10, unique=True)
    ecu_type = models.OneToOneField("EcuType", related_name='ecu_ref_base', on_delete=models.CASCADE, null=True,
                                    blank=True)

    def __str__(self):
        return self.reman_reference


class Batch(models.Model):
    year = models.CharField("années", max_length=1)
    number = models.IntegerField("numéro de lot", validators=[MaxValueValidator(999), MinValueValidator(1)])
    quantity = models.IntegerField('quantité', validators=[MaxValueValidator(999), MinValueValidator(1)])
    batch_number = models.CharField("numéro de lot", max_length=10, blank=True, unique=True)
    active = models.BooleanField(default=True)
    start_date = models.DateField("date de début", null=True)
    end_date = models.DateField("date de fin", null=True)
    created_at = models.DateTimeField(editable=False, auto_now_add=True)
    created_by = models.ForeignKey(User, editable=False, on_delete=models.CASCADE)
    ecu_ref_base = models.ForeignKey(EcuRefBase, on_delete=models.CASCADE)

    def clean(self):
        date = timezone.now()
        if date.year in DICT_YEAR.keys():
            self.year = DICT_YEAR[date.year]
        else:
            raise ValidationError(_('Impossible formatting of the year!'))

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and user.pk:
            self.created_by = user
        number, quantity = str(self.number), str(self.quantity)
        self.batch_number = self.year + "0" * (3 - len(number)) + number + "0" * (3 - len(quantity)) + quantity + "000"
        super(Batch, self).save(*args, **kwargs)

    def __str__(self):
        return self.batch_number


class Default(models.Model):
    code = models.CharField("code defaut", max_length=10, unique=True)
    description = models.CharField("libellé", max_length=200)
    ecu_type = models.ManyToManyField("EcuType", related_name="defaults", blank=True)

    def __str__(self):
        return "{} - {}".format(self.code, self.description)


class Repair(models.Model):

    identify_number = models.CharField("n° d'identification", max_length=10, unique=True)
    product_number = models.CharField("référence", max_length=50, blank=True)
    remark = models.CharField("remarques", max_length=200, blank=True)
    comment = RichTextField("Commentaires action", max_length=500, config_name="comment", blank=True)
    status = models.CharField("status", max_length=50, default='En cours', choices=STATUS_CHOICES)
    quality_control = models.BooleanField("contrôle qualité", default=False)
    checkout = models.BooleanField("contrôle de sortie", default=False)
    closing_date = models.DateTimeField("date de cloture", null=True, blank=True)
    created_at = models.DateTimeField('ajouté le', editable=False, auto_now_add=True)
    created_by = models.ForeignKey(User, related_name="repairs_created", editable=False, on_delete=models.CASCADE)
    modified_at = models.DateTimeField('modifié le', auto_now=True)
    modified_by = models.ForeignKey(User, related_name="repairs_modified", on_delete=models.CASCADE, null=True,
                                    blank=True)
    batch = models.ForeignKey(Batch, related_name="repairs", on_delete=models.CASCADE)
    default = models.ForeignKey("Default", related_name="repairs", on_delete=models.CASCADE, null=True, blank=True)

    def get_absolute_url(self):
        if self.pk:
            return reverse_lazy('reman:edit_repair', args=[self.pk])
        return reverse_lazy('reman:repair_table', get={'filter': 'quality'})

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and user.pk:
            self.created_by = self.modified_by = user
        if not self.pk:
            batch_number = self.identify_number[:-3] + "000"
            self.batch = Batch.objects.get(batch_number__exact=batch_number)
        elif self.pk and self.quality_control:
            prod_ok = Repair.objects.filter(batch=self.batch, quality_control=True).count()
            if self.batch.quantity <= prod_ok:
                self.batch.active = False
                self.batch.save()
        super(Repair, self).save(*args, **kwargs)

    def __str__(self):
        return self.identify_number


class SparePart(models.Model):
    code_produit = models.CharField('code Produit', max_length=100)
    code_magasin = models.CharField('code Magasin', max_length=20, blank=True)
    code_zone = models.CharField('code Zone', max_length=20, blank=True)
    code_site = models.IntegerField('code Site', null=True, blank=True)
    code_emplacement = models.CharField('code Emplacement', max_length=10, blank=True)
    cumul_dispo = models.IntegerField('cumul Dispo', null=True, blank=True)
    repairs = models.ManyToManyField(Repair, related_name='spare_part', blank=True)

    def __str__(self):
        return self.code_produit
