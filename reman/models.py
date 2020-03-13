import datetime

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from crum import get_current_user

from utils.django.urls import reverse_lazy
from utils.conf import DICT_YEAR


class Batch(models.Model):
    year = models.CharField("années", max_length=1)
    number = models.IntegerField("numéro de lot", validators=[MaxValueValidator(999), MinValueValidator(1)])
    quantity = models.IntegerField('quantité', validators=[MaxValueValidator(999), MinValueValidator(1)])
    active = models.BooleanField(default=True)
    start_date = models.DateField("date de début", null=True)
    end_date = models.DateField("date de fin", null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, editable=False, on_delete=models.CASCADE)

    def clean(self):
        date = datetime.datetime.now()
        if date.year in DICT_YEAR.keys():
            self.year = DICT_YEAR[date.year]
        else:
            raise ValidationError(_('Impossible formatting of the year!'))

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and user.pk:
            self.created_by = user
        super(Batch, self).save(*args, **kwargs)

    def __str__(self):
        number, quantity = str(self.number), str(self.quantity)
        return self.year + "0" * (3 - len(number)) + number + "0" * (3 - len(quantity)) + quantity


class EcuModel(models.Model):
    name = models.CharField("modèle produit", max_length=50)

    def __str__(self):
        return self.name


class Repair(models.Model):
    identify_number = models.CharField("numéro d'identification", max_length=10, unique=True)
    batch = models.ForeignKey(Batch, related_name="repairs", on_delete=models.CASCADE)
    product_model = models.ForeignKey(EcuModel, on_delete=models.CASCADE)
    hardware = models.CharField("hardware", max_length=10)
    software = models.CharField("software", max_length=10)
    product_number = models.CharField("référence", max_length=50, blank=True)
    remark = models.CharField("remarques", max_length=1000, blank=True)
    quality_control = models.BooleanField("contrôle qualité", default=False)
    checkout = models.BooleanField("contrôle de sortie", default=False)
    closing_date = models.DateTimeField("date de cloture", null=True, blank=True)
    created_at = models.DateTimeField('Ajouté le', auto_now_add=True)
    created_by = models.ForeignKey(User, related_name="repairs_created", editable=False, on_delete=models.CASCADE)
    modified_at = models.DateTimeField('Modifié le', auto_now=True)
    modified_by = models.ForeignKey(User, related_name="repairs_modified", on_delete=models.CASCADE, null=True, blank=True)

    def get_absolute_url(self):
        if self.pk:
            return reverse_lazy('reman:edit_repair', args=[self.pk])
        return reverse_lazy('reman:repair_table', get={'filter': 'quality'})

    def clean(self):
        if not self.batch.active:
            raise ValidationError(_('There is no more repair file to create for this lot!'))

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and user.pk:
            self.created_by = user
            self.modified_by = user
        if not self.pk:
            number = Repair.objects.filter(batch=self.batch.id).count() + 1
            self.identify_number = self.batch.__str__() + "0" * (3 - len(str(number))) + str(number)
        super(Repair, self).save(*args, **kwargs)

    def __str__(self):
        return self.identify_number


class Comment(models.Model):
    repair = models.ForeignKey(Repair, related_name="comments", on_delete=models.CASCADE)
    value = models.CharField("commentaire", max_length=500)

    def __str__(self):
        return self.value


class SparePart(models.Model):
    code_magasin = models.CharField('code Magasin', max_length=20)
    code_produit = models.CharField('code Produit', max_length=100)
    code_zone = models.CharField('code Zone', max_length=20)
    code_site = models.IntegerField('code Site')
    code_emplacement = models.CharField('code Emplacement', max_length=10)
    cumul_dispo = models.IntegerField('cumul Dispo')
    repairs = models.ManyToManyField(Repair, related_name='spare_part', blank=True)

    def __str__(self):
        return self.code_produit
