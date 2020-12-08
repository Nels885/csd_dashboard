from django.db import models

from squalaetp.models import Xelon
from dashboard.models import UserProfile, User


class Raspeedi(models.Model):

    TYPE_CHOICES = [('RAD', 'Radio'), ('NAV', 'Navigation')]
    CON_CHOICES = [(1, '1'), (2, '2')]
    MEDIA_CHOICES = [
        ('N/A', 'Vide'),
        ('HDD', 'Disque Dur'),
        ('8Go', 'Carte SD 8Go'),
        ('16Go', 'Carte SD 16Go'),
        ('8Go 16Go', 'Carte SD 8 ou 16 Go'),
    ]
    PRODUCT_CHOICES = [
        ('RT4', 'RT4'),
        ('RT5', 'RT5'),
        ('RT6', 'RT6'),
        ('RT6v2', 'RT6 version 2'),
        ('SMEG', 'SMEG'),
        ('SMEGP', 'SMEG+ / SMEG+ IV1'),
        ('SMEGP2', 'SMEG+ IV2'),
    ]

    ref_boitier = models.BigIntegerField('référence boîtier', primary_key=True)
    produit = models.CharField('produit', max_length=20, choices=PRODUCT_CHOICES)
    facade = models.CharField('façade', max_length=2)
    type = models.CharField('type', max_length=3, choices=TYPE_CHOICES)
    dab = models.BooleanField('DAB', default=False)
    cam = models.BooleanField('caméra de recul', default=False)
    dump_peedi = models.CharField('dump PEEDI', max_length=25, blank=True)
    cd_version = models.CharField('version CD', max_length=10, blank=True)
    media = models.CharField('type de média', max_length=20, choices=MEDIA_CHOICES, blank=True)
    carto = models.CharField('version cartographie', max_length=20, blank=True)
    dump_renesas = models.CharField('dump RENESAS', max_length=50, blank=True)
    ref_mm = models.CharField('référence MM', max_length=200, blank=True)
    connecteur_ecran = models.IntegerField("nombre de connecteur d'écran", choices=CON_CHOICES, null=True, blank=True)

    class Meta:
        verbose_name = "Données RASPEEDI"
        ordering = ['ref_boitier']

    def __iter__(self):
        for field in self._meta.fields:
            yield field.verbose_name.capitalize(), field.value_to_string(self)

    def __str__(self):
        return "{} - {} - {} - {}".format(self.ref_boitier, self.produit, self.facade, self.type)


class Programing(models.Model):
    psa_barcode = models.BigIntegerField('référence boîtier', primary_key=True)
    peedi_path = models.CharField('dossier PEEDI', max_length=20)
    peedi_dump = models.CharField('dump PEEDI', max_length=25, blank=True)
    renesas_dump = models.CharField('dump RENESAS', max_length=50, blank=True)
    multimedia = models.OneToOneField('psa.Multimedia', on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Données Programmation"
        ordering = ['psa_barcode']

    def __iter__(self):
        for field in self._meta.fields:
            yield field.verbose_name.capitalize(), field.value_to_string(self)

    def __str__(self):
        return str(self.psa_barcode)


class AddReference(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    add_product = models.ForeignKey(Raspeedi, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class UnlockProduct(models.Model):
    user = models.ForeignKey(UserProfile, editable=False, on_delete=models.CASCADE)
    unlock = models.ForeignKey(Xelon, editable=False, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField('ajouté le', editable=False, auto_now_add=True)
    modified_at = models.DateTimeField('modifié le', auto_now=True)

    class Meta:
        verbose_name = "Déverrouillage VIN"
        ordering = ['-created_at']

    def __str__(self):
        return self.unlock.numero_de_dossier
