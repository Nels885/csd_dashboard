from django.db import models
from django.contrib.auth.models import User


class Raspeedi(models.Model):
    ref_boitier = models.BigIntegerField('référence boîtier', primary_key=True)
    produit = models.CharField(max_length=20)
    facade = models.CharField('façade', max_length=2)
    type = models.CharField(max_length=3)
    dab = models.BooleanField('DAB', default=False)
    cam = models.BooleanField('caméra de recul', default=False)
    dump_peedi = models.CharField('dump PEEDI', max_length=25, null=True)
    cd_version = models.CharField(max_length=10, null=True)
    media = models.CharField('type de média', max_length=20, null=True)
    carto = models.CharField('version cartographie', max_length=20, null=True)
    dump_renesas = models.CharField(max_length=50, null=True)
    ref_mm = models.CharField(max_length=200, null=True)
    connecteur_ecran = models.IntegerField("nombre de connecteur d'écran", null=True)

    def __str__(self):
        return "{} - {} - {} - {}".format(self.ref_boitier, self.produit, self.facade, self.type)

# class AddReference(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     produit_ajoute = models.ForeignKey(Raspeedi, on_delete=models.CASCADE)
#     ajoute_le = models.DateTimeField(auto_now_add=True)
