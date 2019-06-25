from django.db import models

from squalaetp.models import Corvet
from dashboard.models import UserProfile

TYPE_CHOICES = [
    ('RAD', 'Radio'),
    ('NAV', 'Navigation'),
]

CON_CHOICES = [
    (1, '1'),
    (2, '2'),
]

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


class Raspeedi(models.Model):
    ref_boitier = models.BigIntegerField('référence boîtier', primary_key=True)
    produit = models.CharField(max_length=20, choices=PRODUCT_CHOICES)
    facade = models.CharField('façade', max_length=2)
    type = models.CharField(max_length=3, choices=TYPE_CHOICES)
    dab = models.BooleanField('DAB', default=False)
    cam = models.BooleanField('caméra de recul', default=False)
    dump_peedi = models.CharField('dump PEEDI', max_length=25, default="", blank=True)
    cd_version = models.CharField(max_length=10, default="", blank=True)
    media = models.CharField('type de média', max_length=20, choices=MEDIA_CHOICES, null=True)
    carto = models.CharField('version cartographie', max_length=20, default="", blank=True)
    dump_renesas = models.CharField(max_length=50, default="", blank=True)
    ref_mm = models.CharField(max_length=200, default="", blank=True)
    connecteur_ecran = models.IntegerField("nombre de connecteur d'écran", choices=CON_CHOICES, null=True)
    corvets = models.ManyToManyField(Corvet, related_name='raspeedi', blank=True)

    def __str__(self):
        return "{} - {} - {} - {}".format(self.ref_boitier, self.produit, self.facade, self.type)


class AddReference(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    add_product = models.ForeignKey(Raspeedi, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
