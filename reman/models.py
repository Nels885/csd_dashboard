import datetime

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from crum import get_current_user

from utils.conf import DICT_YEAR


class Batch(models.Model):
    year = models.CharField("années", max_length=1)
    number = models.IntegerField("numéro de lot", validators=[MaxValueValidator(999), MinValueValidator(1)])
    quantity = models.IntegerField('quantité', validators=[MaxValueValidator(999), MinValueValidator(1)])
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def clean(self):
        date = datetime.datetime.now()
        if date.year in DICT_YEAR.keys():
            self.year = DICT_YEAR[date.year]
        else:
            raise ValidationError(_('Impossible formatting of the year!'))

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and not user.pk:
            user = None
        self.created_by = user
        super().save(*args, **kwargs)

    def __str__(self):
        return "Batch n°{} du {}".format(self.number, self.created_at.strftime("%d-%m-%Y"))


class Repair(models.Model):
    MODEL_CHOICES = [
        ('EDC15C2', 'EDC15C2'),
        ('EDC17', 'EDC17'),
    ]
    batch_year = models.ForeignKey(Batch, related_name='batch_year', on_delete=models.CASCADE)
    batch_number = models.ForeignKey(Batch, related_name='batch_number', on_delete=models.CASCADE)
    identify_number = models.CharField("numéro d'identification", max_length=10, unique=True)
    product_model = models.CharField("modèle produit", max_length=50, choices=MODEL_CHOICES)
    product_reference = models.CharField("référence produit", max_length=50)
    serial_number = models.CharField("numéro de série", max_length=100, blank=True)
    remark = models.CharField("remarques", max_length=1000, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    quality_control = models.BooleanField("contrôle qualité", default=False)
    checkout = models.BooleanField("contrôle de sortie", default=False)
    closing_date = models.DateTimeField("date de cloture", null=True, blank=True)

    def __str__(self):
        return self.identify_number


class Comment(models.Model):
    repair = models.ForeignKey(Repair, related_name="comments", on_delete=models.CASCADE)
    value = models.CharField("commentaire", max_length=500)

    def __str__(self):
        return self.value
